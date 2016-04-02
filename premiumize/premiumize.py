import requests
import json

from premiumize.filetypes import PremiumizeFile
from premiumize.exceptions import PremiumizeException

class Premiumize:
    """
    Context for the library functions

    @group Folder Operations: *_folder
    @group Item Operations: *_item
    @group Torrent Operations: *_torrent
    @group Transfer Operations: *_transfer
    """

    def __init__(self, user_id, user_pin,
                 base_url="https://www.premiumize.me/api"):
        """
        Initialize the context. Customer ID and PIN can be copied from
        U{https://www.premiumize.me/account}

        @param user_id: Customer ID used to authenticate against the API
        @type user_id: C{str}
        @param user_pin: PIN used to authenticate against the API
        @type user_pin: C{str}
        """
        self.user_id = user_id
        self.user_pin = user_pin
        self.base_url = base_url

    def _request(self, endpoint, params={}):
        """
        Internal method, used for performing HTTP requests.

        @param endpoint: Endpoint portion of the URL, e.g. /folder/list
        @type endpoint: C{str}
        @param params: Additional GET parameters to be added to the request
        @type params: C{dict}

        @return: Data structure with result of the request
        @rtype: C{dict}
        """
        request_params = {
            "customer_id": self.user_id,
            "pin": self.user_pin
        }

        for key in params:
            request_params[key] = params[key]

        req = requests.get(self.base_url + endpoint, params=request_params)

        return json.loads(req.text)

    def list_folder(self, id=None):
        """
        List the contents of a folder

        @param id: ID of the folder that should be listed. If C{id} is not
            given, the contents of the root folder will be listed.
        @type id: C{int}

        @return: Content of the folder
        @rtype: C{list} of L{PremiumizeFile}
        @raise PremiumizeException: if the contents of the folder could not be listed.
        """
        if id is None:
            params = {}
        else:
            params = { "id": id }

        req_res = self._request("/folder/list", params)

        res = []

        if req_res["status"] != "success":
            raise PremiumizeException(req_res["message"])

        for file_dict in req_res['content']:
            res.append(PremiumizeFile(file_dict))

        return res

    def create_folder(self, name, parent_id=None):
        """
        Create a folder called C{name} in the folder with the ID C{parent_id}.
        If C{parent_id} is not given, the folder will be created in the root
        folder.

        @param name: Name of the folder
        @type name: C{str}
        @param parent_id: ID of the parent folder
        @type parent_id: C{int}

        @raise PremiumizeException: if there was an error while creating the
            folder.
        """
        params = {
            "name": name,
        }

        if parent_id is not None:
            params["parent_id"] = parent_id

        req_res = self._request("/folder/create", params=params)

        if not req_res["status"] == "success":
            raise PremiumizeException("Error creating folder: " +
                                      req_res["message"])

    def delete_folder(self, id):
        """
        Delete the folder with the ID C{id}.

        @param id: ID of the folder which should be deleted
        @type id: C{int}

        @raise PremiumizeException: if there was an error deleting the folder
        """
        params = {
            "id": id
        }

        req_res = self._request("/folder/delete", params=params)

        if req_res["status"] == "error":
            raise PremiumizeException("Error deleting folder: " +
                                      req_res["message"])

    def rename_folder(self, id, new_name):
        """
        Renames the folder with the ID C{id} to C{newname}

        @param id: ID of the folder that should be renamed
        @type id: C{id}
        @param new_name: New name of the folder
        @type new_name: C{str}

        @raise PremiumizeException: if there was an error renaming the folder
        """
        params = {
            "id": id,
            "name": new_name
        }

        req_res = self._request("/folder/rename", params=params)

        if req_res["status"] == "error":
            raise PremiumizeException("Error renaming folder: " +
                                      req_res["message"])

    def move_item(self, item, folder_id=None):
        """
        Moves C{item} to the folder with the id C{folder_id}. If C{folder_id}
        is not given, C{item} will be moved into the root folder.

        @param item: Item that should be moved
        @type item: L{PremiumizeFile} or C{list} of L{PremiumizeFile}
        @param folder_id: ID of the folder that C{item} should be moved to
        @type folder_id: C{str}

        @raise PremiumizeException: if there was an error moving the item(s)
        """

        params={}

        if folder_id is not None:
            params['id'] = folder_id

        if type(item) is list:
            for index, i_item in zip(range(len(item)), item):
                if not str(i_item.id) == str(folder_id):
                    params["items[%i][id]" % index] = i_item.id
                    params["items[%i][type]" % index] = i_item.type

            if len(params) < 2:
                # Operation is trivial
                return

        else:
            params["items[0][id]"] = item.id
            params["items[0][type]"] = item.type

        req_res = self._request("/folder/paste", params=params)

        if req_res["status"] == "error":
            raise PremiumizeException("Error moving item: " +
                                      req_res["message"])

    def delete_item(self, item):
        """
        Delete C{item} from the cloud storage

        @param item: item to delete
        @type item: L{PremiumizeFile}

        @raise PremiumizeException: if there was an error deleting the item.
        """
        params = {
            "type": item.type,
            "id": item.id
        }

        req_res = self._request("/item/delete", params=params)

        if req_res["status"] == "error":
            raise PremiumizeException("Error moving item: " +
                                      req_res["message"])

    def browse_torrent(self, item):
        """
        View the contents of a torrent in cloud storage

        @param item: Torrent to view
        @type item: L{PremiumizeFile}

        @return: Contents of the Torrent
        @rtype: C{list} of L{PremiumizeFile}

        @raise PremiumizeException: If there was an error browsing the torrent

        """
        if item.type != "torrent":
            raise PremiumizeException("item is not a torrent")

        params = {
            "hash": item.hash
        }

        req_res = self._request("/torrent/browse", params=params)

        if req_res["status"] == "error":
            raise PremiumizeException("Error browsing torrent: " +
                                      req_res["message"])

        res = []

        for key in req_res['content']:
            for item_name in req_res['content'][key]['children']:
                res.append(
                    PremiumizeFile(req_res['content'][key]['children'][item_name])
                )

        # TODO: Convert to PremiumizeFile recursively
        return res

    def start_transfer(self, source, folder_id=None):
        """
        Start a torrent transfer. The files from the torrent will be written to
        C{folder_id}. If C{folder_id} is not given (or C{None}), the files will
        be written to the root folder.

        @param source: Magnet Link or URL of C{.torrent} file
        @type source: C{str}

        @param folder_id: ID of the folder that the torrent's files should be
            written to.
        @type folder_id: C{int}

        @raise PremiumizeException: If there was an error starting the transfer

        """
        params = {
            "src": source,
            "type": "torrent"
        }

        if folder_id is not None:
            params['folder_id'] = folder_id

        req_res = self._request("/transfer/create", params=params)

        if req_res["status"] == "error":
            raise PremiumizeException("Error starting transfer: " +
                                      req_res["message"])

    def list_transfer(self):
        """
        List all transfers.


        @return: list of structures with transfer information
        @rtype: C{list} of C{dict}
        """
        req_res = self._request("/transfer/list")

        return req_res['transfers']

    def clear_finished_transfer(self):
        """
        Clears finished transfers

        @raise PremiumizeException: If there was an error clearing the finished
            transfers.
        """
        req_res = self._request("/transfer/clearfinished")

        if req_res["status"] == "error":
            raise PremiumizeException("Error starting transfer: " +
                                      req_res["message"])


    def abort_transfer(self, type, id):
        """
        Clears or aborts a transfer

        @param type: Type of the transfer that should be deleted. At the moment
            only C{torrent} is supported
        @type type: C{str}

        @param id: ID of the transfer that should be deleted.
        @type id: C{int}

        @raise PremiumizeException: If there was an error aborting the transfer
        """
        params = {
            "type": type,
            "id": id
        }

        req_res = self._request("/transfer/delete", params=params)

        if req_res["status"] == "error":
            raise PremiumizeException("Error deleting transfer: " +
                                      req_res["message"])
