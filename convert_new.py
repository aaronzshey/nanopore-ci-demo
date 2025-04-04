# detect files in /reference_fastas directory and convert to fasta
# supported files: .docx .rtf .ape .geneious .dna and everything supported by biopython
# by Aaron Shey, Apr 2 2025
import docx2txt
from pathlib import Path
from striprtf.striprtf import rtf_to_text
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import sys
from snapgene_reader import snapgene_file_to_seqrecord
from zipfile import ZipFile
from xml.dom import minidom 


# get all the file types that biopython supports
# brittle, should open a pull request to biopython to add a function to get the supported formats
from Bio.SeqIO import _FormatToWriter

supported_formats = _FormatToWriter.keys()

def write_to_file(filename, text):
    print(f"Writing {filename}")
    with open(filename, "w") as output:
        output.write(text)  

def convert_ape_to_fasta(file, file_name): 
    with open(file) as f:
        first_line = f.readline()

    # Extract the number of base pairs from the first line

    words = first_line.split()

    # the number of base pairs is always followed by the words "bp"
    bp_index = words.index("bp")
    num_base_pairs = words[bp_index - 1]

    # copied from https://www.ncbi.nlm.nih.gov/genbank/samplerecord/
    genbank_first_line_template =  "LOCUS       SCU49845     5028 bp    DNA             PLN       21-JUN-1999"
    # SeqIO.convert("123/reference_fastas/one.ape", "genbank", "out-one.fasta", "fasta")

    genbank_first_line = genbank_first_line_template.replace("5028", num_base_pairs)

    # replace the line

    with open(file) as f:
        lines = f.readlines()

    lines[0] = genbank_first_line + "\n"

    with open(file, "w") as f:
        f.writelines(lines)

    # convert the file to fasta format
    print(f"Converting {file_name} to fasta format")
    SeqIO.convert(file, "genbank", file_name, "fasta")

def geneious_to_fasta(file_path, file_name, file_name_with_fasta):
    print(f"Converting {file_name} to fasta format")
    with ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall('extracted_geneious')   


    geneious_xml = minidom.parse(f"extracted_geneious/{file_name}")

    sequence = geneious_xml.getElementsByTagName("charSequence")[0].firstChild.nodeValue


    # inside the xml file, the tags <description> and <cacheName>
    # provide some more metadata about the file.  However we don't care 
    # about that so we don't use it

    # note that we could just cat sequence > out.fasta to write to 
    # a fasta file.  However, the fasta format is ambiguous on whether or not 
    # newlines, whitespace, etc are permitted and could crash the pipeline later
    # on.  So, we accept the overhead of Biopython as a necessary evil 
    # to ensure that we have a valid fasta file
    seq_record = SeqRecord(Seq(sequence))

    with open(file_name_with_fasta, "w") as output_handle:
        SeqIO.write(seq_record, output_handle, "fasta")

run_id = sys.argv[1]

files = Path(f"{run_id}/reference_fastas/").glob("*")

for file in files:
    # convert to Path so we can use pathlib methods
    file = Path(file)
    # let's say we have a file called reference.docx:

    file_extension = file.suffix.lower() # this returns .docx
    file_name = file.stem # this returns reference
    file_full_name = file.name # this returns reference.docx
    file_path_with_fasta = file.with_suffix(".fasta") # this returns reference.fasta

    if file_extension == ".docx":
        # open full path with docx2txt
        text = docx2txt.process(file)
        write_to_file(file_path_with_fasta, text)

    elif file_extension == ".rtf":
        with open(file, "r") as rtf_file:
            rtf_content = rtf_file.read()


        text = rtf_to_text(rtf_content)
        write_to_file(file_path_with_fasta, text)

    

    elif file_extension == ".fa":
        # Rename .fa file to .fasta
        file.rename(file_path_with_fasta)
        print(f"Renaming {file_full_name} to {file_path_with_fasta}")
    
    elif file_extension == ".dna":
        seqrecord = snapgene_file_to_seqrecord(file)
        with open(file_path_with_fasta, "w") as fasta_file:
            SeqIO.write(seqrecord, fasta_file, "fasta")
        print(f".dna file converted to {file_path_with_fasta}")

    elif file_extension == ".fasta":
        print(f"Reference {file_full_name} already in fasta format")

    elif file_extension[1:] in supported_formats:
        print(f"Converting {file_full_name} to fasta")
        SeqIO.convert(file, file_extension[1:], file_path_with_fasta, "fasta")
    
    # special case for gbk because biopython doesn't use it for some reason
    elif file_extension == ".gbk":
        print(f"Converting {file_full_name} to fasta")
        SeqIO.convert(file, "genbank", file_path_with_fasta, "fasta")
    
    elif file_extension == ".ape":
        convert_ape_to_fasta(file, file_path_with_fasta)
    
    elif file_extension == ".geneious":
        geneious_to_fasta(file, file_full_name, file_path_with_fasta)
    
    else:
        print(f"Unsupported file {file_full_name}")