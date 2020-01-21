# fabmogp
This is a mogp (Multi-Output Gaussian Process Emulator) plugin for [FabSim3](https://github.com/djgroen/FabSim3.git).

## Dependencies:

[mogp_emulator](https://www.github.com/alan-turing-institute/mogp_emulator)

[fdfault](https://www.github.com/egdaub/fdfault)


## Installation
Simply type `fab localhost install_plugin:fabmogp` anywhere inside your FabSim3 install directory.

### FabSim3 Configuration
Once you have installed the required dependencies, you will need to take a few small configuration steps:
1. Go to `(FabSim Home)/deploy`
2. Open `machines_user.yml`
3. Under the section `default:`, please add the following lines:
   <br/> a. `  mpi_exec=(mpiexec_file_path)`
   <br/> _NOTE: you can find it in your local machine by running `which mpiexec` 
   <br/> Please replace `mpiexec_file_path` with your actual install path file._
   <br/> b. `  fdfault_exec=(fdfault Home)`
   <br/> _NOTE: Please replace (fdfault Home) with your actual install directory._
  
## Testing

1. To run a single job, simply type: 
   <br/> `fab localhost localhost mogp:demo`
2. To run the ensemble, you can type, simply type: 
   <br/> `fab localhost mogp_ensemble:demo,sample_points=20`
3. You can copy back any results from completed runs using:
   <br/> `fab localhost fetch_results`
   <br/> The results will then be in a directory inside `(FabSim3 Home)/results`, which is most likely called `demo_localhost_16`
4. You can analysis the simulation output using:
   <br/> `fab localhost mogp_analysis:demo,demo_localhost_16`
