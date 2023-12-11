import time
import subprocess
import psutil


from pywinauto import Application
from pywinauto.findwindows import ElementNotFoundError

APP_PATH = r"C:\Program Files\Common Files\Bentley Shared\CONNECTION Client\Bentley.Connect.Client.exe"


class BentleyClientManager:

    def __init__(
            self,
            username,
            password,
            client_path=r"C:\Program Files\Common Files\Bentley Shared\CONNECTION Client\Bentley.Connect.Client.exe",
            client_title="CONNECTION Client"
    ):
        self._username = username
        self._password = password
        self._client_path = client_path
        self._client_title = client_title
        self._process_id = None
        self._app = None

    @property
    def process_name(self):
        return APP_PATH.rsplit("\\", maxsplit=1)[1]

    @property
    def app(self):
        return self._app

    def set_app(self, app: Application):
        self._app = app

    def process_id(self):
        self._process_id = self._get_pid_by_name()
        return self._process_id

    def main_window(self):
        return self.app.window(title=self._client_title)

    def _get_pid_by_name(self):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == self.process_name:
                return proc.info['pid']
        return None

    def connected_to_client(self):
        if self.process_id() is None:
            return False
        app = Application(backend="uia").connect(process=self._process_id)
        windows = app.windows()

        if windows:
            self.set_app(app)
            return True
        return False

    def connect_to_client(self, timeout=20):
        print("Starting up app...")
        subprocess.Popen(APP_PATH)
        start_time = time.time()
        while time.time() - start_time < timeout:
            print("Checking if app is running in the foreground...")
            if self.connected_to_client():
                break
            time.sleep(1)
        else:
            raise ValueError('Could not find a window, therefore could not connect...')

    def start(self, timeout=20):
        print("Check if an app instance is already running...")
        if self.connected_to_client():
            return
        self.connect_to_client(timeout)
        return

    def logged_in(self):
        authenticated_view = self.main_window().child_window(
            title="Bentley.Connect.Client;component/Views/AuthenticatedView.xaml",
            auto_id="OuterFrame",
            control_type="Pane"
        )
        return authenticated_view.exists()

    def _login(self, timeout=20):
        main_window = self.main_window()
        email_address = main_window.child_window(auto_id="identifierInput", control_type="Edit")
        for try_idx in range(3):
            if email_address.exists():
                break
            email_address = main_window.child_window(auto_id="identifierInput", control_type="Edit")
            another_account_link = main_window.child_window(title="Use another account", control_type="Hyperlink")
            back_button = main_window.child_window(title="Back", control_type="Hyperlink")
            no_network_connection = main_window.child_window(title="No network connection detected",
                                                             control_type="Text")
            if another_account_link.exists():
                another_account_link.click_input()
            elif back_button.exists():
                back_button.click_input()
            elif no_network_connection.exists():
                time.sleep(1)
                continue
            time.sleep(1)
        else:
            raise ConnectionError('No network connection detected. Please contact your administrator.')
        email_address.set_edit_text(self._username)
        print("Email filled...")
        time.sleep(1)
        try:
            popup_exit = main_window.child_window(title="Don't show saved information", control_type="Button")
            popup_exit.click_input()
            print("Popup clicked away...")
        except ElementNotFoundError:
            pass
        next_button = main_window.child_window(title="Next", auto_id='sign-in-button', control_type="Hyperlink")
        next_button.click_input()
        print("Navigating to password input...")
        time.sleep(1)
        password = main_window.child_window(auto_id='password', control_type="Edit")
        password.set_edit_text(self._password)
        print("Password filled...")
        time.sleep(1)
        sign_in_button = main_window.child_window(title="Sign In", auto_id='sign-in-button', control_type="Hyperlink")
        sign_in_button.click_input()
        start_time = time.time()
        while time.time() - start_time < timeout:
            print("Check if logged in...")
            if self.logged_in():
                print("Logged in...")
                return
            time.sleep(1)
        else:
            raise ValueError('Failed to log in... This is either due to wrong credentials, or due to a connection error...')

    def login(self):
        if self.logged_in():
            print("An account is already logged in. First signing out...")
            self._logout()
        try:
            self._login()
        except ElementNotFoundError as e:
            print(e)
            print("Restart process...")
            self.app.kill()
            self.start()
            self.login()

    def check_if_signed_out(self, timeout=10):
        start_time = time.time()
        while time.time() - start_time < timeout:
            print("Checking if account is signed out...")
            if not self.logged_in():
                print("Signed out...")
                break
            time.sleep(1)
        else:
            raise ValueError('Failed to sign out...')

    def _logout(self, timeout=10):
        # Logout
        print("Signing out...")
        _main_window = self.main_window()
        other_actions = _main_window.child_window(title="Settings", auto_id="SettingIcon", control_type="Button")
        other_actions.click()
        time.sleep(2)
        signout = _main_window.child_window(title="Sign Out", control_type="MenuItem")
        signout.click_input()
        self.check_if_signed_out(timeout)
        time.sleep(0.5)

    def logout(self, timeout=10):
        if self.logged_in():
            self._logout(timeout)
        else:
            raise SystemError("The client was already logged out...")


if __name__ == "__main__":
    bentley_client_manager = BentleyClientManager(
        username='user@company.com',
        password='Y0uR-B3Nt13Y-PA$$worD'
    )
    bentley_client_manager.start()
    bentley_client_manager.login()
