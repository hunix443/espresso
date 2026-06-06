<div align="center">
    <h1>Espresso</h1>
    <p>This is a simple command-line password manager that uses 
    AES-256-GCM authenticated encryption and Argon2id key derivation</p>
</div>

# Quickstart

I'll try to update this tab as quickly as possible when releasing a new version, this project might not get as much updates once I'm done with the features I thought of.

```sh
# I'll implement the Bash command soon, 
# lemme finish up the basic features first
```

## Guide

To understand how the app works and understand what it actually does,
this is where your password will be stored

```sh
~/.espresso-vault/vault.json
```

By using the owner mods 0600, allowing only you to access its content, except if you're an admin of course.

The vault.json file will look like this :

```json
{
  "version": 1,
  "kdf": {
    "name": "argon2id",
    "salt": "q64/W1JkJ7fg8hEsJSVZvA=="
  },
  "cipher": {
    "name": "aes-256-gcm",
    "nonce": "XCOuDgwctCqHvnI4",
    "ciphertext": "9Heaah09oEZ7PKksKL5AADpV"
  }
}⏎  
```

:white_flag: | Be aware that once you set your master password there is no way to retrieve your password
if you forget it.

## Contributing

Not sure if there are lots of thing to work on with my password manager but
still, if y'all wants to add pretty visuals, themes, features that maybe other
people may find useful, feel free to fork and open a PR, I'd be extremely happy to see other people  

Anyway hope this project will help some of y'all. Feel free to use Espresso as a self project for you to build your way in cybersecurity.