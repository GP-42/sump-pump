# How to setup keyring

> [!IMPORTANT]
> I know that this setup requires an interactive user session for the services to run. However, I prefer this solution above having passwords in a clear text flat file like ```.env```.
> I'm still investigating on how to do this with a system service running a D-Bus session.

## Why using the PAM setup for keyring?

We don't want to enter a password every first time we need to access the keyring to retrieve a password. Luckily, something like a login keyring exists. The login keyring is automatically created when first logging on using the PAM config.

## Prerequisites

The following packages have to be installed via *Add/Remove Software* or ```apt```:
- GNOME keyring services (daemon and tools)  
```gnome-keyring```  
*This package is generally installed when RPi is installed with a GUI.*
- PAM module to unlock the GNOME keyring upon login  
```libpam-gnome-keyring```

## PAM config

### To log on locally
When logging on directly on the RPi, the following lines should exist in ```/etc/pam.d/login```:  
- in the ```auth``` section:  
```auth optional pam_gnome_keyring.so```
- in the ```session``` section:  
```session optional pam_gnome_keyring.so auto_start```

### To log on via RDP
When logging on to the RPi via RDP, the file ```/etc/pam.d/xrdp-sesman``` has to be adapted to look like this:  
```
#%PAM-1.0
auth required pam_env.so readenv=1
auth required pam_env.so readenv=1 envfile=/etc/default/locale
@include common-auth
auth optional pam_gnome_keyring.so
@include common-account
@include common-session
session optional pam_gnome_keyring.so auto_start
@include common-password
```  

### Reboot

After you changed the required files you have to reboot for the changes to take effect.

## Checking the login keyring

You can check the keyring via the ```seahorse``` package.  
*This package is generally installed when RPi is installed with a GUI.*  
1. Although the package has a GUI, you have to launch it from a terminal. A GUI will launch, but the terminal where you started the package is now blocked until you close the application window.
2. On the left hand side, under the header *Passwords*, you should now see the ```Login``` keyring. You should notice that, even though we didn't do anything yet, the keyring is already unlocked (the icon on the right hand side of the name is an open lock).
3. However, before we can use the keyring with our project, we have to make it the default keyring. This is done by right-clicking the ```Login``` keyring and choosing *Set as default* from the context menu.

## Initializing the keyring

1. Open the Python script ```sump-pump/scripts/init_keyring.py```.
2. Replace ```YourPasswordGoesHere``` on every line with the resp. password
3. Save the file.
4. Execute the Python script ```sump-pump/scripts/init_keyring.py```.
5. The entries appear in the ```Login``` keyring.
6. Don't forget to delete the passwords in the script again.

## Keyring file location
On RPi the user keyrings are located in ```/home/myUser/.local/share/keyrings```.  
