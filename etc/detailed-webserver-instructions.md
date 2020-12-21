## Hosting a pheweb and accessing it from your browser

Run `pheweb serve --open`.  That command should either open a browser to your new PheWeb, or it should give you a URL that you can open in your browser to access your new PheWeb.  If it doesn't, follow the directions for [hosting a PheWeb and accessing it from your browser](etc/detailed-webserver-instructions.md).

- If port 5000 is already taken, choose a different port (for example, 5432) and run `pheweb serve --port 5432` instead.

- If the server works but you can't open it in a web browser, you have two options:

  1. Run PheWeb on the open internet.

     You need a port that can get through your firewall. 80 or 5000 probably work.

     - To use port 80 you'll need root permissions, so run something like  `sudo $(which python3) $(which pheweb) serve --port 80`.

     Then run `pheweb serve --guess-address` and open the two URLs it provides.

  2. Run PheWeb with the default settings, then use an SSH tunnel to connect to it from your computer.

     For example, if you normally ssh in with `ssh watman@x.example.com`, then the command you should run (on the computer you're sitting at) is `ssh -N -L localhost:5000:localhost:5000 watman@x.example.com`.

     Then open <http://localhost:5000> in your web browser.  It should connect straight to port 5000 on the server through your ssh server, allowing you to access your PheWeb.



## Using Apache2 or Nginx

At this point your PheWeb should be working how you want it to, except maybe the URL you're using.

`pheweb serve` already uses gunicorn. For maximum speed and safety, you should run gunicorn routed through a reverse proxy like Apache2 or Nginx. If you choose Apache2, I have some documentation [here](etc/detailed-apache2-instructions/README.md).



## Using OAuth

1. Make your own random `SECRET_KEY` for flask.

   ```bash
   $ python3 -c 'import os; print(os.urandom(24))'
   b'(\x1e\xe5IY\xe4\xdc\x00s\xc6z\xf8\x9b\xf3\x99Miw\x9dct\xdf}\xeb'
   ```

   In `config.py` in your pheweb directory, set

   ```python
   SECRET_KEY = '(\x1e\xe5IY\xe4\xdc\x00s\xc6z\xf8\x9b\xf3\x99Miw\x9dct\xdf}\xeb'
   ```

2. Set up OAuth with Google.

   Go [here](https://console.developers.google.com/apis/credentials) to create a project.
   In the list "Authorized redirect URIs" add your OAuth callback URL, which should look like `http://example.com/callback/google` or `http://example.com:5000/callback/google`.

   In `config.py`, set:

   ```python
   login = {
     'GOOGLE_LOGIN_CLIENT_ID': 'something-something.apps.googleusercontent.com',
     'GOOGLE_LOGIN_CLIENT_SECRET': 'letters-letters',
     'whitelist': [
       'user1@example.com',
       'user2@example.com',
       'user3@gmail.com',
     ]
   }
   ```

   The correct values of `GOOGLE_LOGIN_CLIENT_ID` and `GOOGLE_LOGIN_CLIENT_SECRET` are at the top of the Google project page.  The whitelist can contain any email addresses connected to Google accounts.



## Using Google Analytics

Go [here](https://analytics.google.com/analytics/web) and do whatever you have to to get your own UA-xxxxxxxx-x tracking id.

Then, in `config.py`, set:

```
GOOGLE_ANALYTICS_TRACKING_ID = 'UA-xxxxxxxx-x'
```

and kill and restart `pheweb serve`.

If you visit your site, you should see the activity at [the Google Analytics web console](https://analytics.google.com/analytics/web).
