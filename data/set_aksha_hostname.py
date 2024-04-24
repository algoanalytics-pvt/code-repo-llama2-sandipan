import socket
import os

def create_and_save_host(file_name, file_content):
  if not os.path.exists(file_name):
    # Create the file.
    with open(file_name, 'w') as f:
      f.write(file_content)

  # Save the content to the file.
  with open(file_name, 'w') as f:
    f.write(file_content)


if __name__ == '__main__':
    hostname = socket.getfqdn() #socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    confirm  = input("Looks like your hostname IP address: " + ip_address + " please confirm: y/N? ")

    if confirm == 'y': 
          pass
    else: 
       ip_address = input("Enter new IP address or Hostname: ");
    ip_address.strip();
    create_and_save_host('Aksha/etc/host', ip_address) 