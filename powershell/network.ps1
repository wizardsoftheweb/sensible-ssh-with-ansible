<#
.SYNOPSIS
    Creates or destroys a virtual network to use with Vagrant
.DESCRIPTION
    Hyper-V doesn't play well with Vagrant. It completely ignores networking
    configuration. This script sets up or destroys a virtual switch and assigns
    all the necessary components to use it.
.PARAMETER Switch
    The name of the switch to create
.PARAMETER LeadingThree
    The first three octets of the desired switch IP
.PARAMETER PreferIpv6
    If not set, removes the IPv6 config
.PARAMETER Create
    True if the network should be created
.PARAMETER Destroy
    True if the network should be destroyed
.EXAMPLE
    ./network.ps1 -Create

.EXAMPLE
    ./network.ps1 -Create -Verbose
    VERBOSE: Creating VMSwitch NATWotwSsh
    VERBOSE: Creating vEthernet (NATWotwSsh) IPv4 address 10.47.1.1
    VERBOSE: Disabling vEthernet (NATWotwSsh) IPv6 address
    VERBOSE: Creating NetNat NATWotwSsh
.EXAMPLE
    ./network.ps1 -Destroy

.EXAMPLE
    ./network.ps1 -Destroy
    VERBOSE: Removing VMSwitch NATWotwSsh
    VERBOSE: Removing NetNat NATWotwSsh
.LINK
    https://www.vagrantup.com/docs/hyperv/limitations.html
.LINK
    https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/user-guide/setup-nat-network
#>
[CmdletBinding()]
Param(
    [string] $Switch = "NATWotwSsh",
    [string] $NetAdapterName = (Get-NetAdapter | Where-Object {$_.AdminStatus -eq "Up" -and $_.ConnectorPresent -eq "True" -and $_.InterfaceOperationalStatus -eq 1}).Name,
    [string] $LeadingThree = "10.47.1",
    [switch] $PreferIpv6 = $false,
    [switch] $Create = $false,
    [switch] $Destroy = $false
    )

# https://stackoverflow.com/a/11440595
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    $arguments = "& '" + $myInvocation.myCommand.definition + "'"
    Start-Process powershell -Verb runAs -ArgumentList $arguments
    break
}

Get-VMSwitch -SwitchName "$Switch" 2>&1 | Out-Null
$SwitchResult = $?
if ($Create -and ($SwitchResult -eq $false)) {
    Write-Verbose "Creating VMSwitch $Switch on $NetAdapterName"
    New-VMSwitch -Name "$Switch" -NetAdapterName "$NetAdapterName" -AllowManagementOS $true -MinimumBandwidthMode None | Out-Null
}
if ($Destroy -and ($SwitchResult -eq $true)) {
    Write-Verbose "Removing VMSwitch $Switch"
    Remove-VMSwitch -Name "$Switch" -Force | Out-Null
}

Get-NetIPAddress -InterfaceAlias "vEthernet ($Switch)" -AddressFamily IPv4 2>&1 | Out-Null
$IpResult = $?
if ($Create -and ($IpResult -eq $false)) {
    Write-Verbose "Creating vEthernet ($Switch) IPv4 address $LeadingThree.1"
    $Adapter = Get-NetAdapter -Name "vEthernet ($Switch)"
    New-NetIPAddress -IPAddress "$LeadingThree.1" -AddressFamily IPv4 -PrefixLength 24 -InterfaceIndex $Adapter.ifIndex | Out-Null
    # if (-not $PreferIpv6) {
    #     Write-Verbose "Disabling vEthernet ($Switch) IPv6"
    #     Disable-NetAdapterBinding -Name "vEthernet ($Switch)" -ComponentID ms_tcpip6 -Confirm:$false 2>&1 | Out-Null
    # }
}
# It seems like PowerShell does this automatically; any error output is
# redirected to Out-Null as well
if ($Destroy -and ($IpResult -eq $true)) {
    Write-Verbose "Removing vEthernet ($Switch)"
    Remove-NetIPAddress -InterfaceAlias "vEthernet ($Switch)" -Confirm:$false 2>&1 | Out-Null
}

Get-NetNat -Name "$Switch" 2>&1 | Out-Null
$NatResult = $?
if ($Create -and ($NatResult -eq $false)) {
    Write-Verbose "Creating NetNat $Switch"
    New-NetNat -Name "$Switch" -InternalIPInterfaceAddressPrefix "$LeadingThree.0/24" | Out-Null
}
if ($Destroy -and ($NatResult -eq $true)) {
    Write-Verbose "Removing NetNat $Switch"
    Remove-NetNat -Name "$Switch" -Confirm:$false | Out-Null
}
