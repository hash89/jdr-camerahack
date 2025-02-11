# jdr-camerahack
Camera hack app for life-size role-playing game

# Installation
```sh
az webapp up --name hack-camera --runtime "PYTHON:3.10" --sku F1
```

```sh
az webapp deployment github-actions add --repo "hash89/jdr-camerahack" --resource-group hadrien.puissant_rg_7446 --branch master --name hack-camera --login-with-github
```

s