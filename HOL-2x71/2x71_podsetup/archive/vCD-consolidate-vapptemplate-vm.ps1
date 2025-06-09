<#
Brandon Bazan https://ifitisnotbroken.wordpress.com/
This script is designed to gather the Org, Catalog, vAppTemplate, VM(optional) to ensure there is only 1 value to consolidate
It will check the power state since it will only work against powered off VMs
Assumes that you are already connected to a Cloud Director instance
#>
#User Input:
Write-Host -ForegroundColor Green " `n **************************************************************************************"
$org_name = Read-host -Prompt ' Input the Org name'
$catalog = Read-host -Prompt ' Input the Catalog name'
$vApp_template_name = Read-host -Prompt ' Input the vApp Template name'
$VM_input = Read-Host -Prompt ' Input the VM name, leave blank if you wish to consolidate the entire vApp Template'
Write-Host -ForegroundColor Green " `n **************************************************************************************"
$Power_state = Get-Org $org_name | Get-Catalog -name $catalog | Get-CIVAppTemplate -Name $vapp_template_name
if(!$VM_input){
    #Checking power state, if powered off it will consolidate and report progress
    If($Power_state.Status -eq 'PoweredOff' -or $Power_state.Status -eq 'Resolved'){
      $consolidate_vapptemplate = Get-Org -Name $org_name | Get-Catalog $catalog | Get-CIVAppTemplate -Name $vApp_template_name | Get-CIVMTemplate | where {$_.Extensiondata.vCloudExtension.any.VirtualDisksMaxChainLength -ne 1} | Get-CIView
          If(!$consolidate_vapptemplate){
            Write-Host -ForegroundColor Yellow " `n ******************************************************************************* `n"
            Write-Host -ForegroundColor Green "  Could not consolidate vApp Template: $vApp_template_name chain length of 1`n"
            Write-Host -ForegroundColor Yellow " `n ******************************************************************************* `n"
            }else{     
              Foreach ($vm in $consolidate_vapptemplate) {   
                Write-Output "Processing VM: $($VM.name)"  
                try {   
                    $task = $VM.Consolidate_Task()  
                    Start-Sleep 1  
                    while ((Get-Task -Id $task.Id).State -ne "Success" ) {  
                        #Report power state
                        Write-Output "$($VM.name) - Percent: $((Get-Task -Id $task.Id).PercentComplete) / State: $((Get-Task -Id $task.Id).State)"   
                        Start-Sleep .5
                        }   
                    } catch {   
                        Write-Output "      $($VM.name) Failed!"   
                        }    
               }#End Foreach loop
            }
    }elseif($Power_state.status -eq 'PoweredOn'){
        Write-Host -ForegroundColor Yellow " `n ******************************************************************************* `n"
        Write-Host -ForegroundColor Green "  Could not consolidate vApp Template: $vApp_template_name since it is powered on`n"
        Write-Host -ForegroundColor Yellow " `n ******************************************************************************* `n" 
    }else{
        Write-Host -ForegroundColor Yellow " `n ******************************************************************************* `n"
        Write-Host -ForegroundColor Green "  Could not consolidate vApp Template: $vApp_template_name`n"
        Write-Host -ForegroundColor Green "  Please check on this vApp Template and run again `n"
        Write-Host -ForegroundColor Yellow " `n ******************************************************************************* `n"
        }#End else checking if powered off
}else{
    #Checking power state, if powered off it will consolidate and report progress
    If($Power_state.Status -eq 'PoweredOff' -or $Power_state.Status -eq 'Resolved'){
      $consolidate_vm = Get-Org -Name $org_name | Get-Catalog $catalog | Get-CIVAppTemplate -Name $vApp_template_name | Get-CIVMTemplate $VM_input | where {$_.Extensiondata.vCloudExtension.any.VirtualDisksMaxChainLength -ne 1} | Get-CIView

      #Foreach ($vm in $consolidate_vm) {   
        Write-Output "Processing VM: $($VM.name)"  
        try {   
            $task = $consolidate_vm.Consolidate_Task()  
            Start-Sleep 1  
            while ((Get-Task -Id $task.Id).State -ne "Success" ) {  
                #Report power state
                Write-Output "$($consolidate_vm.name) - Percent: $((Get-Task -Id $task.Id).PercentComplete) / State: $((Get-Task -Id $task.Id).State)"   
                Start-Sleep .5
                }   
            } catch {   
                Write-Output "      $($vm.name) Failed!"   
                }    
      # }#End Foreach loop
    }elseif($Power_state.status -eq 'PoweredOn' -or $Power_state -eq 'Unresolved'){
        Write-Host -ForegroundColor Yellow " `n ************************************************************************************************************* `n"
        Write-Host -ForegroundColor Green "  Could not consolidate $VM_input within vApp Temaplte $vApp_template_name since it is powered on`n"
        Write-Host -ForegroundColor Yellow " `n ************************************************************************************************************* `n" 
    }elseif($Power_state.Extensiondata.vCloudExtension.any.VirtualDisksMaxChainLength -eq 1){
        Write-Host -ForegroundColor Yellow " `n ************************************************************************************************************* `n"
        Write-Host -ForegroundColor Green "  Could not consolidate $VM_input within vApp Temaplte $vApp_template_name since it has a chain length of 1`n"
        Write-Host -ForegroundColor Yellow " `n **************************************************************** `n"
    }else{
        Write-Host -ForegroundColor Yellow " `n ************************************************************************************************************* `n"
        Write-Host -ForegroundColor Green "  Could not consolidate VM $VM_input within vApp Temaplte $vApp_template_name`n"
        Write-Host -ForegroundColor Green "  Please check on this VM and run again `n"
        Write-Host -ForegroundColor Yellow " `n ************************************************************************************************************* `n"
        }#End else checking if powered off
}
