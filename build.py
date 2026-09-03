#!/usr/bin/env python3
"""Render templates/about.html with content.yml into docs/ for GitHub Pages."""

import yaml, os, shutil, filecmp, sys, logging
from jinja2 import Environment, FileSystemLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", stream=sys.stdout)
logger = logging.getLogger(__name__)

def main():
    """Render templates/about.html with content.yml into docs/ for GitHub Pages."""
    html = prepare_html(content_file_name="content.yml")
    logger.info("Prepared HTML from content.yml and templates/about.html")

    prepare_docs()
    build_pages(html)

def prepare_html(content_file_name):
    """Render templates/about.html with content.yml into docs/ for GitHub Pages."""
    with open(content_file_name, "r") as f:
        content = yaml.safe_load(f)

    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("about.html")
    html = template.render(**content)
    return html

def prepare_docs():
    """Prepare docs/ for GitHub Pages."""
    logger.info("Preparing docs/ for GitHub Pages")
    os.makedirs("docs", exist_ok=True)
    os.makedirs("docs/static", exist_ok=True)
    open("docs/.nojekyll", "w").close()
    logger.info("Prepared docs/ directory.")

def sync_static(dcmp):
    """Sync static files to docs/static/ for GitHub Pages."""
    logger.info("Syncing static files to docs/static/")
    for name in dcmp.left_only:
        src_path = os.path.join(dcmp.left, name)
        dst_path = os.path.join(dcmp.right, name)
        if os.path.isdir(src_path):
            logger.info(f"Copying directory {src_path} to {dst_path}")
            shutil.copytree(src_path, dst_path)
        else:
            logger.info(f"Copying file {src_path} to {dst_path}")
            shutil.copy2(src_path, dst_path)

    for name in dcmp.common_files:
        src_path = os.path.join(dcmp.left, name)
        dst_path = os.path.join(dcmp.right, name)
        if not filecmp.cmp(src_path, dst_path, shallow=False):
            logger.info(f"Updating file {src_path} to {dst_path}")
            shutil.copy2(src_path, dst_path)

    for name in dcmp.right_only:
        dst_path = os.path.join(dcmp.right, name)
        if os.path.isdir(dst_path):
            logger.info(f"Removing directory {dst_path}")
            shutil.rmtree(dst_path)
        else:
            logger.info(f"Removing file {dst_path}")
            os.remove(dst_path)

    for sub_dcmp in dcmp.subdirs.values():
        logger.info(f"Recursing into subdirectory {sub_dcmp.left} and {sub_dcmp.right}")
        sync_static(sub_dcmp)


def build_pages(html):
    """Build pages for GitHub Pages."""
    with open("docs/index.html", "w") as f:
        f.write(html)
    
    sync_static(filecmp.dircmp("static", "docs/static"))
    

if __name__ == "__main__":
    main()