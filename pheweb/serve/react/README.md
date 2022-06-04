# Build UI

Pull recent version

```
git pull
```

Remove previous libraries

```
rm -rf node_modules
```

Install npm libraries

```
npm install
```

Build UI

```
npm run build
```

# Local server

There are thre options described below running it locally, via
port forwarding pointing to an existing server.
## Set your pheweb root

Set your pheweb root

```
	export PHEWEB_ROOT=<YOUR PHEWEB ROOT>
```


Run server
```
    export PYTHONPATH=$PHEWEB_ROOT:$PYTHONPATH
	run_pheweb.py pheweb serve --port 9999 --num-workers=3
```

# Remote server

## ssh port forward

on port 9999


```
	ssh -L9999:localhost:9999 $API_HOST
```

## Point to existing server

edit public/config.js

Set the root property under application to your rest end point


Start front end

```npm start```


# Troubleshooting

Error: error:0308010C:digital envelope routines::unsupported

```
export NODE_OPTIONS=--openssl-legacy-provider
```
