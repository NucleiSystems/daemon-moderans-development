import logging
import subprocess
from typing import Optional
import typing

from fastapi import Depends, HTTPException

from ..users.auth_utils import get_current_user
from ..users.user_models import User

from ..storage_service.ipfs_model import DataStorage
from ..users.user_handler_utils import get_db


def get_user_cids(user_id, db) -> list:
    """
    It returns a list of all the DataStorage objects that have the same owner_id as the user_id passed in

    Arguments:

    * `user_id`: the user's id
    * `db`: SQLAlchemy database object

    Returns:

    A list of DataStorage objects
    """

    try:
        return db.query(DataStorage).filter(DataStorage.owner_id == user_id).all()
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


def get_collective_bytes(user_id: int, db) -> int:
    """
    It takes a user_id and a database session as input, and returns the sum of the file_size of all the
    DataStorages that have the same owner_id as the user_id

    Arguments:

    * `user_id`: int
    * `db`: Session = Depends(get_db)

    Returns:

    The sum of the file_size of all the records that belong to the user_id
    """

    try:
        query = db.query(DataStorage).filter(DataStorage.owner_id == user_id).all()
        return sum(record.file_size for record in query)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


def paginate_using_gb(
    user_id: int,
    db,
    page_size: Optional[None | int] = 10,
    page: Optional[None | int] = 1,
) -> list[list[DataStorage]]:
    """
    A function that divides the records into pages which is a nested list with the size of the nested
    list's record being determined through the files record's file_size adding up to a gigabyte

    Arguments:

    * `user_id`: the user's id
    * `db`: a database connection
    * `page_size`: the number of records per page
    * `page`: int = 1

    Returns:

    A list of lists of DataStorage objects.
    """

    try:
        # get all the records that belong to the user_id
        records = get_user_cids(user_id, db)
        # sort the records by file_size
        records.sort(key=lambda x: x.file_size, reverse=True)
        # get the collective bytes
        collective_bytes = get_collective_bytes(user_id, db)
        # get the number of pages
        pages = collective_bytes // (1024**3) + 1
        # initialize an empty list
        paginated_records = []
        # initialize the start and end index
        start = 0
        end = 0
        # loop through the number of pages
        for _ in range(pages):
            # set the end index to be the start index + page_size
            end = start + page_size
            # append the records from the start index to the end index
            paginated_records.append(records[start:end])
            # set the start index to be the end index
            start = end
        # return the paginated records
        return paginated_records
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


file_bytes_type = typing.NewType(
    "file_bytes_type",
    list[
        dict[
            User.id,
            DataStorage.file_name,
            DataStorage.file_type,
            bytes,
        ]
    ],
)


class UserDataExtraction:
    def __init__(self, user_id):
        """
        I'm trying to get the user_id from the token, and then use that user_id to get the user's cids
        from the database

        Arguments:

        * `user_id`: User = Depends(get_current_user)
        """
        self.user_id: User = Depends(get_current_user)
        if not self.user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        if self.user_id == user_id:

            self.db = Depends(get_db)
            self.user_data = get_user_cids(self.user_id, self.db)
            self.file_bytes: file_bytes_type = []

    def file_bytes_serializer(self):
        # use file_byte_generator to get the file_bytes and append it to the file_bytes list
        # return the file_bytes list

        for file_byte in self.file_byte_generator():
            self.file_bytes.append(
                {
                    "user_id": self.user_id,
                    "file_name": self.user_data.file_name,
                    "file_type": self.user_data.file_type,
                    "file_bytes": file_byte,
                }
            )

    def download_file_ipfs(self, cid: str, record: DataStorage):
        """
        It downloads a file from IPFS using the local ipget executable

        Arguments:

        * `cid`: the content identifier of the file
        * `record`: DataStorage = field(metadata={"data_key": "record"})
        """
        # use subprocess the download the file using the local ipget executable and return the files bytes
        file_bytes = subprocess.run(
            ["ipget", "-o", "-", cid], capture_output=True, text=True
        ).stdout

    def file_byte_generator(self):
        # generator which yields the file bytes from the function download_file_ipfs
        for record in self.user_data:
            yield self.download_file_ipfs(record.cid, record)

    def get_file_bytes(self):
        return self.file_bytes
