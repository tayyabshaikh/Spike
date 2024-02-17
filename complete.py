import subprocess
import os
import time

#spike_path = os.getenv('SPIKE')
#print(spike_path)
#pk_path = os.getenv('pk')
#print(pk_path)


def create_text_file(file_path, num_iterations, pc_value):
    try:
        with open(file_path, 'w') as file:
            file.write(f"until pc 0 {pc_value}\n")
            for i in range(num_iterations):
                file.write("run 1\n")
                file.write("reg 0\n")
        print(f"Text file '{file_path}' created successfully with {num_iterations} iterations.")
    except Exception as e:
        print(f"An error occurred: {e}")

def compile_and_run_riscv_program():
    # Ask user to input RISC-V assembly file
    assembly_file_path = input("Enter the RISC-V assembly file name (with .s extension): ")
    assembly_file = os.path.basename(assembly_file_path)

    output_dir = input("Enter the path to the output(Instructions) directory: ")
    output_file = os.path.join(output_dir, assembly_file.replace('.s', '.txt'))
    
    # Ask user to input Spike architecture
    #spike_architecture = input("Enter the Spike architecture: ")

    # Compile RISC-V assembly file
    compile_command = f"riscv32-unknown-elf-gcc {assembly_file} -o {assembly_file.replace('.s', '')}"
    subprocess.run(compile_command, shell=True)

    #Create dump file
    dump_file = f"riscv32-unknown-elf-objdump -t {assembly_file.replace('.s', '')} > {assembly_file.replace('.s', '.dump')}"
    subprocess.run(dump_file, shell=True)
    
    # Get PC address using objdump
    objdump_command = f"riscv32-unknown-elf-objdump -t {assembly_file.replace('.s', '')} | grep main"
    objdump_result = subprocess.check_output(objdump_command, shell=True).decode('utf-8')
    pc_address = objdump_result.split()[0]
   
    main_file = f"riscv32-unknown-elf-objdump --disassemble=main {assembly_file.replace('.s','')} > {output_file}"
    main_result = subprocess.check_output(main_file, shell=True).decode('utf-8')
    # Open the file in read mode
    with open(output_file, 'r') as file:
        line_count = sum(1 for line in file)
    print(line_count-7)
      
    #main_file1 = f"riscv32-unknown-elf-objdump --disassemble=main {assembly_file.replace('.s','')}"
    #main_result = subprocess.check_output(main_file, shell=True).decode('utf-8')
    
    file_path = input("Enter file name with Path: ")
    num_iterations = line_count-7
    create_text_file(file_path, num_iterations, pc_address)

    a = subprocess.check_output(f"spike -d --debug-cmd={file_path} $pk {assembly_file.replace('.s', '')}",shell=True)
    #time.sleep(2)
    #a.terminate()
    
def convert_hex_to_binary(input_file, output_file):
    # Open the input file for reading
    with open(input_file, "r") as infile:
        # Read all lines from the file
        hex_lines = infile.readlines()

        # Open the output file for writing
        with open(output_file, "w") as outfile:
            # Process each line
            for hex_value in hex_lines:
                # Remove any leading/trailing whitespace and newline characters
                hex_value = hex_value.strip()
                
                # Convert hexadecimal to binary
                binary_value = bin(int(hex_value, 16))[2:].zfill(32)  # Convert hex to int, then int to binary string
                
                # Write the binary value to the output file
                outfile.write(binary_value + '\n')

def main():
    filename = input("Enter File Name To Load Instructions: ")
    #Construct the command with proper escaping or using single quotes
    file = f" awk 'NR >= 8 {{print $2}}' {filename}.txt > opcodes.txt"
    waitt = subprocess.Popen(file, shell=True)
    waitt.wait
    input_file = "opcodes.txt"
    output_file = "binary_values.txt"
    output_dir = input("Enter Address to read binary instructions from: ")
    output_file_complete = os.path.join(output_dir,output_file )
    convert_hex_to_binary(input_file,output_file_complete)

    top_module_dir = input("Enter top module address: ")
    top_file = input("Enter TOP file name: ")
    output_top_file = os.path.join(top_module_dir,top_file)

    commands = [
        f"quartus_map --read_settings_files=on --write_settings_files=off {output_top_file} -c {output_top_file}",
        f"quartus_fit --read_settings_files=off --write_settings_files=off {output_top_file} -c {output_top_file}",
        f"quartus_asm --read_settings_files=off --write_settings_files=off {output_top_file} -c {output_top_file}",
        f"quartus_sta {output_top_file} -c {output_top_file}",
        f"quartus_eda --read_settings_files=off --write_settings_files=off {output_top_file} -c {output_top_file}",
        "qsta_default_script.tcl version: #1",  
        f'quartus_sh -t "/home/tayyab/intelFPGA_lite/22.1std/quartus/common/tcl/internal/nativelink/qnativesim.tcl" --rtl_sim "{top_file}" "{top_file}"'
    ]

    # Run all commands together
    for command in commands:
        subprocess.run(command, shell=True)


if __name__ == "__main__":
    compile_and_run_riscv_program()
    main()