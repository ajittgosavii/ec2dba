import math

class EC2DatabaseSizingCalculator:
    # AWS instance types with AMD preference
    INSTANCE_TYPES = [
        # AMD-based instances (preferred for cost savings)
        {"type": "m6a.large", "vCPU": 2, "RAM": 8, "max_ebs_bandwidth": 4750, "family": "general", "processor": "AMD"},
        {"type": "m6a.xlarge", "vCPU": 4, "RAM": 16, "max_ebs_bandwidth": 9500, "family": "general", "processor": "AMD"},
        {"type": "m6a.2xlarge", "vCPU": 8, "RAM": 32, "max_ebs_bandwidth": 19000, "family": "general", "processor": "AMD"},
        {"type": "m6a.4xlarge", "vCPU": 16, "RAM": 64, "max_ebs_bandwidth": 38000, "family": "general", "processor": "AMD"},
        {"type": "m6a.8xlarge", "vCPU": 32, "RAM": 128, "max_ebs_bandwidth": 47500, "family": "general", "processor": "AMD"},
        {"type": "r6a.large", "vCPU": 2, "RAM": 16, "max_ebs_bandwidth": 4750, "family": "memory", "processor": "AMD"},
        {"type": "r6a.xlarge", "vCPU": 4, "RAM": 32, "max_ebs_bandwidth": 9500, "family": "memory", "processor": "AMD"},
        {"type": "r6a.2xlarge", "vCPU": 8, "RAM": 64, "max_ebs_bandwidth": 19000, "family": "memory", "processor": "AMD"},
        {"type": "r6a.4xlarge", "vCPU": 16, "RAM": 128, "max_ebs_bandwidth": 38000, "family": "memory", "processor": "AMD"},
        {"type": "r6a.8xlarge", "vCPU": 32, "RAM": 256, "max_ebs_bandwidth": 47500, "family": "memory", "processor": "AMD"},
        {"type": "c6a.large", "vCPU": 2, "RAM": 4, "max_ebs_bandwidth": 4750, "family": "compute", "processor": "AMD"},
        {"type": "c6a.xlarge", "vCPU": 4, "RAM": 8, "max_ebs_bandwidth": 9500, "family": "compute", "processor": "AMD"},
        {"type": "c6a.2xlarge", "vCPU": 8, "RAM": 16, "max_ebs_bandwidth": 19000, "family": "compute", "processor": "AMD"},
        {"type": "c6a.4xlarge", "vCPU": 16, "RAM": 32, "max_ebs_bandwidth": 38000, "family": "compute", "processor": "AMD"},
        {"type": "c6a.8xlarge", "vCPU": 32, "RAM": 64, "max_ebs_bandwidth": 47500, "family": "compute", "processor": "AMD"},
        
        # Intel-based instances (fallback options)
        {"type": "m6i.large", "vCPU": 2, "RAM": 8, "max_ebs_bandwidth": 4750, "family": "general", "processor": "Intel"},
        {"type": "m6i.xlarge", "vCPU": 4, "RAM": 16, "max_ebs_bandwidth": 9500, "family": "general", "processor": "Intel"},
        {"type": "m6i.2xlarge", "vCPU": 8, "RAM": 32, "max_ebs_bandwidth": 19000, "family": "general", "processor": "Intel"},
        {"type": "m6i.4xlarge", "vCPU": 16, "RAM": 64, "max_ebs_bandwidth": 38000, "family": "general", "processor": "Intel"},
        {"type": "m6i.8xlarge", "vCPU": 32, "RAM": 128, "max_ebs_bandwidth": 47500, "family": "general", "processor": "Intel"},
        {"type": "r6i.large", "vCPU": 2, "RAM": 16, "max_ebs_bandwidth": 4750, "family": "memory", "processor": "Intel"},
        {"type": "r6i.xlarge", "vCPU": 4, "RAM": 32, "max_ebs_bandwidth": 9500, "family": "memory", "processor": "Intel"},
        {"type": "r6i.2xlarge", "vCPU": 8, "RAM": 64, "max_ebs_bandwidth": 19000, "family": "memory", "processor": "Intel"},
        {"type": "r6i.4xlarge", "vCPU": 16, "RAM": 128, "max_ebs_bandwidth": 38000, "family": "memory", "processor": "Intel"},
        {"type": "r6i.8xlarge", "vCPU": 32, "RAM": 256, "max_ebs_bandwidth": 47500, "family": "memory", "processor": "Intel"},
        {"type": "c6i.large", "vCPU": 2, "RAM": 4, "max_ebs_bandwidth": 4750, "family": "compute", "processor": "Intel"},
        {"type": "c6i.xlarge", "vCPU": 4, "RAM": 8, "max_ebs_bandwidth": 9500, "family": "compute", "processor": "Intel"},
        {"type": "c6i.2xlarge", "vCPU": 8, "RAM": 16, "max_ebs_bandwidth": 19000, "family": "compute", "processor": "Intel"},
        {"type": "c6i.4xlarge", "vCPU": 16, "RAM": 32, "max_ebs_bandwidth": 38000, "family": "compute", "processor": "Intel"},
        {"type": "c6i.8xlarge", "vCPU": 32, "RAM": 64, "max_ebs_bandwidth": 47500, "family": "compute", "processor": "Intel"},
    ]
    
    # Environment multipliers
    ENV_MULTIPLIERS = {
        "PROD": {"cpu_ram": 1.0, "storage": 1.0},
        "SQA": {"cpu_ram": 0.75, "storage": 0.7},
        "QA": {"cpu_ram": 0.6, "storage": 0.5},
        "DEV": {"cpu_ram": 0.4, "storage": 0.3}
    }
    
    def __init__(self):
        self.inputs = {
            "on_prem_cores": 16,
            "peak_cpu_percent": 65,
            "on_prem_ram_gb": 64,
            "peak_ram_percent": 75,
            "storage_current_gb": 500,
            "storage_growth_rate": 0.15,
            "peak_iops": 8000,
            "peak_throughput_mbps": 400,
            "years": 3,
            "workload_profile": "general",
            "prefer_amd": True  # Default to cost-optimized AMD instances
        }
    
    def calculate_requirements(self, env):
        """Calculate requirements for a specific environment"""
        mult = self.ENV_MULTIPLIERS[env]
        
        # Calculate compute requirements
        vcpus = self.inputs["on_prem_cores"] * (self.inputs["peak_cpu_percent"] / 100)
        vcpus = vcpus * (1 + 0.2) / 0.7 * mult["cpu_ram"]
        vcpus = math.ceil(vcpus)
        
        ram = self.inputs["on_prem_ram_gb"] * (self.inputs["peak_ram_percent"] / 100)
        ram = ram * (1 + 0.2) / 0.7 * mult["cpu_ram"]
        ram = math.ceil(ram)
        
        # Calculate storage requirements
        growth_factor = (1 + self.inputs["storage_growth_rate"]) ** self.inputs["years"]
        storage = self.inputs["storage_current_gb"] * growth_factor
        storage = storage * (1 + 0.3) * mult["storage"]
        storage = math.ceil(storage)
        
        # Calculate I/O requirements
        iops_required = self.inputs["peak_iops"] * (1 + 0.3)
        iops_required = math.ceil(iops_required)
        
        throughput_required = self.inputs["peak_throughput_mbps"] * (1 + 0.3)
        throughput_required = math.ceil(throughput_required)
        
        # Determine EBS type
        ebs_type = "io2" if (iops_required > 16000 or throughput_required > 1000) else "gp3"
        
        # Select instance
        instance = self.select_instance(vcpus, ram, throughput_required, self.inputs["workload_profile"])
        
        return {
            "environment": env,
            "instance_type": instance["type"],
            "vCPUs": vcpus,
            "RAM_GB": ram,
            "storage_GB": storage,
            "ebs_type": ebs_type,
            "iops_required": iops_required,
            "throughput_required": f"{throughput_required} MB/s",
            "family": instance["family"],
            "processor": instance["processor"]
        }
    
    def select_instance(self, required_vcpus, required_ram, required_throughput, workload_profile):
        """Select appropriate EC2 instance with AMD preference for cost savings"""
        candidates = []
        
        for instance in self.INSTANCE_TYPES:
            # Filter by workload profile
            if workload_profile != "general" and instance["family"] != workload_profile:
                continue
                
            # Check if meets minimum requirements
            if (instance["vCPU"] >= required_vcpus and 
                instance["RAM"] >= required_ram and
                instance["max_ebs_bandwidth"] >= (required_throughput * 1.2)):
                candidates.append(instance)
        
        # If no candidates found, return largest available
        if not candidates:
            return max(self.INSTANCE_TYPES, key=lambda x: x["vCPU"])
        
        # Prioritize AMD for cost savings if enabled
        if self.inputs["prefer_amd"]:
            amd_candidates = [i for i in candidates if i["processor"] == "AMD"]
            if amd_candidates:
                # Return smallest AMD instance that meets requirements
                return min(amd_candidates, key=lambda x: x["vCPU"])
        
        # Return smallest Intel instance if AMD preference disabled or no AMD options
        return min(candidates, key=lambda x: x["vCPU"])
    
    def generate_all_recommendations(self):
        """Generate recommendations for all environments"""
        results = {}
        for env in self.ENV_MULTIPLIERS.keys():
            results[env] = self.calculate_requirements(env)
        return results

    def run_interactive(self):
        """Run in interactive mode to collect user inputs"""
        print("\n===== SQL Server EC2 Sizing Calculator =====")
        print("Provide your on-premise SQL Server metrics:")
        
        self.inputs["on_prem_cores"] = int(input("Number of CPU cores: ") or 16)
        self.inputs["peak_cpu_percent"] = float(input("Peak CPU utilization (%): ") or 65)
        self.inputs["on_prem_ram_gb"] = int(input("Total RAM (GB): ") or 64)
        self.inputs["peak_ram_percent"] = float(input("Peak RAM utilization (%): ") or 75)
        self.inputs["storage_current_gb"] = int(input("Current DB storage (GB): ") or 500)
        self.inputs["storage_growth_rate"] = float(input("Annual storage growth rate (decimal): ") or 0.15)
        self.inputs["peak_iops"] = int(input("Peak IOPS: ") or 8000)
        self.inputs["peak_throughput_mbps"] = float(input("Peak throughput (MB/s): ") or 400)
        self.inputs["years"] = int(input("Growth projection (years): ") or 3)
        
        print("\nWorkload profile:")
        print("1. General (balanced)")
        print("2. Memory-optimized (data warehouse, analytics)")
        print("3. Compute-optimized (OLTP, high transactions)")
        profile_choice = input("Select (1-3): ") or "1"
        
        profiles = {"1": "general", "2": "memory", "3": "compute"}
        self.inputs["workload_profile"] = profiles.get(profile_choice, "general")
        
        # AMD preference option
        amd_choice = input("\nPrefer AMD-based instances for cost savings? (Y/n): ") or "Y"
        self.inputs["prefer_amd"] = amd_choice.upper() in ["Y", "YES"]
        
        return self.generate_all_recommendations()

# Main execution
if __name__ == "__main__":
    calculator = EC2DatabaseSizingCalculator()
    results = calculator.run_interactive()
    
    print("\n" + "="*50)
    print("EC2 SIZING RECOMMENDATIONS")
    print("="*50)
    
    cost_savings_note = ""
    for env, spec in results.items():
        print(f"\n{env} ENVIRONMENT:")
        print(f"  Instance Type:   {spec['instance_type']}")
        print(f"  vCPUs:           {spec['vCPUs']}")
        print(f"  RAM (GB):        {spec['RAM_GB']}")
        print(f"  Storage (GB):    {spec['storage_GB']} ({spec['ebs_type']})")
        print(f"  Processor:       {spec['processor']}")
        print(f"  IOPS Required:   {spec['iops_required']}")
        print(f"  Throughput:      {spec['throughput_required']}")
        print(f"  Workload Family: {spec['family'].capitalize()}-optimized")
        
        # Add cost savings note for AMD
        if "AMD" in spec['processor']:
            cost_savings_note = "\nNOTE: AMD-based instances selected for cost savings (typically 10-20% cheaper than comparable Intel instances)"
    
    print("\nADDITIONAL CONSIDERATIONS:")
    print("- For PROD: Implement Multi-AZ deployment and enable RPO/RTO protections")
    print("- Use gp3 for cost-effective general storage, io2 for high-performance needs")
    print("- Monitor with CloudWatch and adjust based on actual usage patterns")
    print("- Consider Reserved Instances for PROD environments for cost savings")
    print("- Enable EBS encryption and regular snapshots for all environments")
    
    if cost_savings_note:
        print(cost_savings_note)
    
    print("\nCost Optimization Tip: AMD-based instances (m6a, r6a, c6a) typically offer")
    print("better price/performance. Validate exact pricing using AWS Pricing Calculator.")