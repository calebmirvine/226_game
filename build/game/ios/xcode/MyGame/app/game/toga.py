# code taken from https://github.com/beeware/toga/tree/main/examples/positron-django
import asyncio
import os
import socketserver
from threading import Thread
from wsgiref.simple_server import WSGIServer


import django
from django.core import management as django_manage
from django.core.handlers.wsgi import WSGIHandler
from django.core.servers.basehttp import WSGIRequestHandler
from django.contrib.staticfiles.handlers import StaticFilesHandler


import toga
from toga.style import Pack
from toga.style.pack import CENTER, COLUMN, ROW


class ThreadedWSGIServer(socketserver.ThreadingMixIn, WSGIServer):
    pass


class Game(toga.App):

    def web_server(self) -> None:
        """
        This function starts a web server to serve the Django application.
        It sets up the Django environment, applies migrations, and starts the server.
        """
        try:
            self.paths.data.mkdir(exist_ok=True)
            db_path = self.paths.data / "db.sqlite3"
            os.environ["DJANGO_DB_PATH"] = str(db_path)

            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")
            django.setup(set_prefix=False)


            print("Applying database migrations...")
            django_manage.call_command("migrate")

            print("Starting server...")
            # Use port 0 to let the server select an available port.
            self._httpd = ThreadedWSGIServer(("127.0.0.1", 0), WSGIRequestHandler)
            self._httpd.daemon_threads = True

            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")

            wsgi_handler = WSGIHandler()
            #Wrap the handler in static files handler (for our css)
            self._httpd.set_app(StaticFilesHandler(wsgi_handler))

            # The server is now listening, but connections will block until serve_forever is run.
            self.loop.call_soon_threadsafe(self.server_exists.set_result, "ready")
            self._httpd.serve_forever()
        except Exception as e:
            print(f"Error starting server: {e}")
            import traceback
            traceback.print_exc()

    def cleanup(self, app: toga.App) -> None:
        """
        This function shuts down the web server.
        """
        print("Shutting down...")
        self._httpd.shutdown()
        return True

    def startup(self) -> None:
        """
        This function starts the web server and creates the main window.
        It also creates the URL bar and the web view.
        """
        self.server_exists = asyncio.Future()

        self.web_view = toga.WebView()

        self.server_thread = Thread(target=self.web_server)
        self.server_thread.start()

        self.on_exit = self.cleanup

        # Create URL bar (To allow  search to access certain game functionality)
        
        self.url_input = toga.TextInput(value="Starting server...", style=Pack(flex=1))
        self.url_input = toga.TextInput(value="Starting server...", style=Pack(flex=1))
        self.go_button = toga.Button("Go", on_press=self.load_url, style=Pack(width=50, margin_left=5))
        url_box = toga.Box(
            children=[self.url_input, self.go_button],
            style=Pack(direction=ROW, margin=5)
        )
        #Disabled for now, we dont really need it here
        url_box.enabled = False

        self.web_view.style = Pack(flex=1)

        # Create main box
        main_box = toga.Box(
            children=[url_box, self.web_view],
            style=Pack(direction=COLUMN)
        )


        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    def load_url(self, widget) -> None:
        """
        This function loads the URL in the web view.
        """
        url = self.url_input.value
        if url.startswith(("http://", "https://")):
            self.web_view.url = url
        else:
            print(f"Invalid URL ignored: {url}")

    async def on_running(self) -> None:
        """
        This function runs when the app is running.
        """
        await self.server_exists

        host, port = self._httpd.socket.getsockname()
        url = f"http://{host}:{port}/game/"
        self.web_view.url = url
        self.url_input.value = url

        self.main_window.show()


def main() -> toga.App:
    """
    This function returns the app.
    """
    return Game("Treasure Hunt Board Game")