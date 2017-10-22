# -*- mode: ruby -*-
# vi: set ft=ruby :

HostOptions = Struct.new(
  :hostname
  )

Vagrant.configure('2') do |config|
  config.vm.box = 'centos/7'
  config.vm.network "public_network", bridge: "Default Switch"
  # controller.vm.network "private_network", type: "dhcp"

  config.vm.define 'controller' do |controller|
    box_name = 'ansible_controller'

    controller.vm.provider 'virtualbox' do |virtualbox|
      virtualbox.name = box_name
    end

    controller.vm.provider 'hyperv' do |hyperv|
      hyperv.vmname = box_name
    end

    controller.vm.provision 'file', source: './provisioning', destination: '/tmp/provisioning'

    if Vagrant::Util::Platform.windows? then
      controller.vm.provision 'shell' do |sh|
        sh.path = 'windows-provision.sh'
        sh.args = ['vagrant']
        sh.privileged = true
      end
    else
      controller.vm.provision 'ansible' do |ansible|
        ansible.playbook = 'provisioning/main.yml'
      end
    end
  end

  network = [
    HostOptions.new("trantor"),
    HostOptions.new("terminus"),
    HostOptions.new("kalgan")
  ]

  network.each do |machine|
    config.vm.define machine.hostname do |virtual_machine|
      virtual_machine.vm.hostname = machine.hostname

      virtual_machine.vm.provider 'virtualbox' do |virtualbox|
        virtualbox.name = machine.hostname
      end

      virtual_machine.vm.provider 'hyperv' do |hyperv|
        hyperv.vmname = machine.hostname
      end
    end
  end
end
