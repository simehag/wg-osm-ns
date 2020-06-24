# wg-osm-ns
This repository contains the files associated with the network service launched in my thesis at NTNU (TTM4905).

# Deployment
To deploy the network service, first set up a [Charmed OSM](https://jaas.ai/tutorials/charmed-osm-get-started#1-introduction) platform. 
The VDU uses Ubuntu 18.04, so download an [Ubuntu 18.04 image](https://cloud-images.ubuntu.com/bionic/) and upload it to your VIM.



Compress the VNF and NS package, and upload them to OSM.
```bash
osm upload-package vWireGuard_vnf.tar.gz
osm upload-package vWireGuard_ns.tar.gz
```

Instantiate the network service.
```bash
osm ns-create --ns_name vWireGuard_ns --nsd_name vWireGuard_nsd --vim_account <INSERT_VIM_ACCOUNT> --config '{additionalParamsForVnf: [{"member-vnf-index": "1", additionalParams: { gateway_ip: 10.0.9.1} }, {"member-vnf-index": "2", additionalParams: { gateway_ip: 10.0.9.2} } ] }'
```

# Reference
@mastersthesis{Haga2020, title={{Towards 5G network slice isolation with WireGuard and Open Source MANO}}, author={Haga, Simen}, year={2020}, school={Norwegian University of Science and Technology (NTNU)} }
