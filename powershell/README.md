
# PowerShell Components for Virtual Networking

Hyper-V doesn't [play well with others](https://www.vagrantup.com/docs/hyperv/limitations.html). I found [a solid hack](https://github.com/hashicorp/vagrant/issues/7915#issuecomment-286874774) to address it. I tried following [a solid write-up](https://www.thomasmaurer.ch/2016/05/set-up-a-hyper-v-virtual-switch-using-a-nat-network/), and, eventually, even [the official docs](https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/quick-start/connect-to-network), but I have yet to get it to work.

<!-- MarkdownTOC -->

- [Warning](#warning)
- [Vagrant](#vagrant)
- [Network Only](#networkonly)
- [Setup](#setup)
- [Issues](#issues)

<!-- /MarkdownTOC -->


## Warning

This code adds some virtual networking stuff. The parts that work will temporarily remove your connection as it updates. The other parts will break your connection. If any of the network issues persist, you can manually remove the switch from Hyper-V Manager > Virtual Switch Manager and reset your connection to the proper network/adapter in Control Panel > Network and Internet > Network and Sharing Center.

## Vagrant

You’ll need Hyper-V enabled, recent PowerShell, and Vagrant. Open PowerShell as Administrator here and run

```powershell
# This should break network connectivity
PS$ vagrant up --provider=hyperv
# This should restore it
PS$ vagrant destroy
```

You can manually pick the switch by removing the `controller.vm.network...` line in the hyperv provider section. During `vagrant up`, you’ll be prompted to select the switch, which should populate with a list of everything available in Hyper-V.

## Network Only

I’ve isolated the networking script, which you can run (inside the same directory) with

```powershell
# Connection goes down
PS$ ./network.ps1 -Create
# Connection returns
PS$ ./network.ps1 -Destroy
# Full explanation
PS$ Get-Help ./network.ps1 -Full
```

## Setup

Hyper-V has a default switch, Default Switch, that seems to be magic. [Using `New-VMSwitch`](https://docs.microsoft.com/en-us/powershell/module/hyper-v/new-vmswitch), I set up a new switch, `NATWotwSsh`, using what I think is the correct configuration. By “I think”, I mean I compared
```powershell
PS$ Get-VMSwitch -Name "Default Switch" | Format-List
```
to
```powershell
PS$ Get-VMSwitch -Name "NATWotwSsh" | Format-List
```
They seem to be identical. Default Switch communicates with the outside world without explicitly setting my NIC (via `NetAdapterName`, I guess). `NATWotwSsh` takes over my NIC (won’t run without `NetAdapterName`) and refuses to communicate with the outside world ([even with `-AllowManagementOS`](https://docs.microsoft.com/en-us/windows-server/virtualization/hyper-v/get-started/create-a-virtual-switch-for-hyper-v-virtual-machines#BKMK_WPS)). To add insult to injury, [creating a switch through the GUI](https://docs.microsoft.com/en-us/windows-server/virtualization/hyper-v/get-started/create-a-virtual-switch-for-hyper-v-virtual-machines#BKMK_HyperVMan), `New Virtual Switch`, seems to work the same way `Default Switch` does. Its config via `Get-VMSwitch | Format-List` seems to be identical to the other two. It does take over my NIC, but it actually shares it.

## Issues

1. `Default Switch` isn't universal; confirmed with sysadmins at work. It's created during the setup of the Hyper-V role.
2. Anecdotally, not setting up `Default Switch` initially gives you the ability to share the host NIC as desired. I watched this happen with two VMs.
3. Anecdotally, setting up `Default Switch` initially removes the ability to share the host NIC easily. I watched a coworker build one via the GUI without it working; I can't get it work in PS but I can with the GUI.
4. I'm most likely missing something simple, probably related to what it's doing with the computer.
