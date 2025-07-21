rm -rf dist build *.egg-info
python -m build --wheel
scp dist/grand_selve*.whl ubuntu@grandselve.app:/home/ubuntu/grand_selve/server
