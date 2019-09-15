import random
import pickle
import os.path
import glob
import re
import string


class CookieStore:
    """
    Class responsible for cookies handling
    """

    # TODO: add search if there is valid cookie and cleanup
    def __init__(self, path: str = '') -> None:
        """
        Initialize variables
        Args:
            path: path to directory where cookies are stored
        """
        self._fname = None  #: string:
        self._path = path

    def save(self, cookie):
        """
        Function to store cookie
        Args:
            cookie: raw cookie data

        Returns:
            file name

        """
        # TODO: rework to handle 3 tries withou success (maybe handled by returning none in case correct filename was not found but is hard to read

        for i in range(3):
            # v.3.6.3 fname = './cookies/COOKIE_'+''.join(random.choices(ascii_uppercase + digits, k=8))
            fname = './cookies/COOKIE_'+''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

            if not os.path.isfile(os.path.join(self._path, fname)):
                self._fname = fname
                break
        try:
            with open(self._fname, 'wb') as f:
                pickle.dump(cookie, f)
        except (FileExistsError, FileExistsError):
            None
            # TODO: add handling with no cookies or keep it so api will be aware that cookie was not created
        return self._fname

    def load(self, fname: str = None):
        """
        Loads cookie file

        Args:
            fname: cookie name

        Returns:
            cookie decoded to raw format

        """
        # todo handle if there wil be none and self fname will be not used
        if fname is None:
            fname = self._fname
        with open(fname, 'rb') as f:
            return pickle.load(f)

    def checkCookies(self):
        """
        Checks if cookie file exist and if more cookies are present

        Returns:
            True: if cookie file exist
            False: if cookie file doesnt exist

        """

        listOfFiles = glob.glob('cookies/*')
        if not listOfFiles:
            return False
        latestFile = max(listOfFiles, key=os.path.getctime)
        self._fname = latestFile
        regex = re.compile(''.join([r'^(?!.*', re.escape(self._fname), r').*$']))
        oldCookies = [i for i in listOfFiles if regex.search(i)]
        self.deleteCookie(oldCookies)
        return True

    def deleteCookie(self, cookie=None):
        """
        Removes cookie file, no action is done if there are no old cookies and no current cookie

        Args:
            cookie: cookie file name

        Returns:

        """
        if cookie is None and self._fname is not None:
            cookie = [self._fname, ]

            for fname in cookie:
                try:
                    os.remove(fname)
                except FileNotFoundError:
                    pass




