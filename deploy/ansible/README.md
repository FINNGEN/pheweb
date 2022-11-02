* install plugins

```
ansible-galaxy collection install community.mysql
ansible-galaxy collection install community.docker
ansible-galaxy collection install ansible.posix
```

* provision server

```
ansible-playbook site.yml -i inventory.ini -u ${USER}  --limit <<your host>>
```
