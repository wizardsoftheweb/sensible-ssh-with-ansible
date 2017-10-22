# -*- mode: ruby -*-
# vi: set ft=ruby :

HYPER_V_SWITCH = 'Default Switch'

Vagrant.configure('2') do |config|

  config.vm.define 'controller' do |controller|
    box_name = 'ansible_controller'

    controller.vm.box = 'centos/7'
    controller.vm.network 'private_network', type: 'dhcp'

    controller.vm.provider 'virtualbox' do |virtualbox|
      virtualbox.name = box_name
    end

    controller.vm.provider 'hyperv' do |hyperv|
      hyperv.vmname = box_name
      controller.vm.network 'public_network', bridge: HYPER_V_SWITCH
    end

    controller.vm.provision 'file', source: './provisioning', destination: '/tmp/provisioning'

    if Vagrant::Util::Platform.windows?
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

  machines = ['trantor', 'terminus', 'kalgan']

  machines.each do |machine|
    config.vm.define machine do |virtual_machine|
      virtual_machine.vm.box = 'centos/7'
      virtual_machine.vm.hostname = machine
      virtual_machine.vm.network 'private_network', type: 'dhcp'

      virtual_machine.vm.provider 'virtualbox' do |virtualbox|
        virtualbox.name = machine
      end

      virtual_machine.vm.provider 'hyperv' do |hyperv|
        hyperv.vmname = machine
        virtual_machine.vm.network 'public_network', bridge: HYPER_V_SWITCH
      end
    end
  end
end
