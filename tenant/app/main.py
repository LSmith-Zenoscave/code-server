from starlette.applications import Starlette
from starlette.responses import JSONResponse, RedirectResponse
from starlette.routing import Route
from starlette.templating import Jinja2Templates
from starlette.background import BackgroundTask

from io import BytesIO

import os
import docker
import asyncio
import logging

host = f'{os.environ["IDE_SUBDOMAIN"]}.{os.environ["DOMAIN_NAME"]}'
docker_network = f"{os.environ['COMPOSE_PROJECT_NAME']}_default"
templates = Jinja2Templates(directory="templates")
app = Starlette(debug=True)

client = docker.from_env()

states = {}

@app.route('/', methods=["GET"])
async def ide(request):
    user_id = request.headers['remote-user']
    states[user_id] = states.get(user_id, 'STARTING')
    task = BackgroundTask(start_code_server, user_id)
    message = "Please wait... your browser will auto refresh when ready"

    if states[user_id] != 'READY':
        return templates.TemplateResponse('ide.html', {
            'request': request,
            'user_id': user_id,
            'state': states[user_id],
            'message': message,
        }, background=task)
    else:
        resp = RedirectResponse(url=f'/')
        resp.set_cookie('remote-user', user_id, 10000, 10000)
        return resp

async def start_code_server(user_id):
    code_name = f'code-{user_id}'
    conf = f"""
[http]
  [http.routers]
    [http.routers.{user_id}]
      rule = "Host(`{host}`) && HeadersRegexp(`cookie`, `.*remote-user={user_id}.*`)"
      middlewares = ["secured", "ssl-header"]
      service = "code-server-{user_id}"
      [http.routers.{user_id}.tls]
        certResolver = "le"
  [http.services]
    [http.services.code-server-{user_id}]
      [[http.services.code-server-{user_id}.loadBalancer.servers]]
         url = "http://code-{user_id}:8080"
"""

    with open(f"/route_conf/{user_id}.toml", "wb") as toml_file:
        toml_file.write(conf.encode('utf-8'))

    states[user_id] = "READY"

    try:
        container = client.containers.get(code_name)
        states[user_id] = 'READY'
        print(container.id)
        return
    except docker.errors.NotFound:
        pass

    try:
        volume = client.volumes.get(code_name)
    except docker.errors.NotFound:
        volume = client.volumes.create(code_name)
    image = client.images.build(
        path='./coder',
        tag=f'code_server/{code_name}',
        pull=True,
        forcerm=True,
        nocache=True,
        buildargs={
            'CODER_USER': user_id
        }
    )

    container = client.containers.run(
        f"code_server/{code_name}",
        name=code_name,
        detach=True,
        command=["--auth", "none"],
        volumes={code_name: {'bind': f'/home/{user_id}/project', 'mode': 'rw'}},
        network=docker_network,
    )

    cids = [c.id for c in client.containers.list()]
    while container.id not in cids:
        cids = [c.id for c in client.containers.list()]
        await asyncio.sleep(3.0)
