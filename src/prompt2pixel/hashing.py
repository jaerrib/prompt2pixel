import hashlib


class HashConverter:
    def __init__(self):
        self.hash_functions = {
            "sha256": hashlib.sha256,
            "sha384": hashlib.sha384,
            "sha512": hashlib.sha512,
            "sha3_256": hashlib.sha3_256,
            "sha3_384": hashlib.sha3_384,
            "sha3_512": hashlib.sha3_512,
            "blake2b": hashlib.blake2b,
            "blake2s": hashlib.blake2s,
        }

    def text_to_hash(self, text: str, hash_type: str, salt: str) -> str:
        if hash_type not in self.hash_functions:
            raise ValueError(
                f"Unsupported hash type. Supported types: {', '.join(self.hash_functions.keys())}"
            )
        return self.hash_functions[hash_type]((text + salt).encode()).hexdigest()

    @staticmethod
    def hash_to_dec(hash_string: str) -> list[int]:
        integer_list: list[int] = []
        for i in range(0, len(hash_string) - 1, 2):
            c: str = hash_string[i] + hash_string[i + 1]
            dec: int = int(c, 16)
            integer_list.append(dec)
        return integer_list
