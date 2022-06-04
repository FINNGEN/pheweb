* Setting up a dev host
   1. on your host machine
      Install ansible.
      ```ansible --version
	  ```
	  The version is important you should have.

      > ansible [core 2.12.4]

   2. create a 'debian 10' instance
   ```
	export dev_host="<YOUR HOST>"
   ```
   3. get the key to your instance
   ```
	   gcloud compute config-ssh
   ```

   4.ssh to your instance
   ```
      ssh ${dev_host}
   ```


   5. create an ansible inventory files that point to your instance
      Please do not use the inventory.ini
	  e.g. my instance is mmaasha-tmp.europe-west1-b.phewas-development
   ```
   export host='<YOUR HOST NAME>'
   echo -e "[development_servers]\n${dev_host} ansible_host=${dev_host}" > dev.ini
   ```
   6. provision using ansible
   run the following command
   ```
   ansible-playbook site.yml -i dev.ini -u ${USER} -vvvv
   ```

   7. in your home directory should be pheweb
      ~/Work/pheweb

   ```
   cd /mnt/nfs/pheweb/example
   export PYTHONPATH=~/Work/pheweb:$PYTHONPATH
   ~/pheweb/pheweb/run_pheweb.py pheweb serve --port 8080 --num-workers=3
   ```
