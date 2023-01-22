from cryptography.fernet import Fernet

key = ""
with open("secret.txt") as f:
    key = f.readline()
print(key)
fern = Fernet(key)
message = "This is the password"
encMessage = fern.encrypt(message.encode())
print("original string: ", message)
print("encrypted string: ", encMessage)

# decrypt the encrypted string with the
# Fernet instance of the key,
# that was used for encrypting the string
# encoded byte string is returned by decrypt method,
# so decode it to string with decode methods
decMessage = fern.decrypt(encMessage).decode()

print("decrypted string: ", decMessage)