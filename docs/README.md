# Docs with Sphinx

## Building


However, if you have need to test locally you may not want to use a virtualenv
or install dependencies.
To build the documentation run:

```
make html
```

Cleaning up the generated documentation files is sometimes necessary before
changes are apparent such as when new reStructuredText files are added, this
can be done with:

```
make clean
```

Whether you use the local approach or the Docker container, when you
finish you should then be able to cd into `build/html` on your local machine
and preview with your browser of choice:

```
cd docs/build/html
python -m http.server 9999
```

Then open your browser to [http://127.0.0.1:9999](http://127.0.0.1:9999)

## With Dockerfile

### Create Docker image "docs-sphere"

```
cd docs
docker build -t docs-sphere .

```

### Run container "docs-sphere"

```
sudo docker run -d -p 8080:80 docs-sphere
```

## Without Dockerfile

```
docker run --name docs-sphere -v source-of-the-html-folder:/usr/share/nginx/html:ro -d -p 8080:80 nginx
```

for my case:
```
sudo docker run --name docs-sphere -v /home/oac/Dev/sphere/dev_sphere/SPHERE/docs/build/html/:/usr/share/nginx/html:ro -d -p 8080:80 nginx
```