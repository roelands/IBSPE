# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 14:00:41 2017

@author: roelands

Comment:
2017-11-03 Add comment lines

"""
def get_lines_from_file( filename ):
# function get_lines_from_file
    try:
        f = open( filename )
    except:
        print('could not open file: ' + filename)
    else:
        lines = []
        for line in f:
            lines.append( line )
        f.close()
    
        return lines

def get_data_blocks(lines):
# function: get_data_blocks
    block_index = []
    k = 0
    split_line = []
    while k in range(len(lines)):
        split_line = lines[k].split()
        if len(split_line) > 1:
            if (split_line[1] == 'DATABLOCK') & (split_line[0]== '%'):
                block_index.append(k)
        k = k + 1
    
    blocks = []
    for i in range(len(block_index)-1):
        blocks.append(lines[block_index[i]:block_index[i+1]])
    # add last block too
    blocks.append(lines[block_index[-1]:])
    return blocks

def read_data_block(block):
# block have the following fields:
# GLOBAL (some global name)
# TYPE (the type definition)
# NAME (list of field names)
# SEPARATOR ()
# DIM (data size rows*colums)
    fields = ('DATABLOCK', 'GLOBAL', 'TYPE', 'NAME', 'SEPARATOR', 'DIM')
    block_definition = dict.fromkeys(fields)
    raw_data = []
    split_line = []
    for line in block:
#        print(line)
        if len(line) > 0: # there can be empty lines
            if line[0][0] == '%': # definition
                split_line = line.split()
#                print(split_line)
                for f in fields:
                    if split_line[1] == f:
                        block_definition[f] = split_line[2:]
#                        print(content[f])
            else:
                raw_data.append(line)

    return block_definition, raw_data

def verify_block_definition( block_definition ):
# def verify_block_definition( block_definition )

    supported_separators = ('"~', '"\\t', '"=')
    verified_definition = {}
    definition_valid = True
    # seperator is the field that needs to be present.
    if block_definition['SEPARATOR'] == None:
        print('ERROR: no separator found in DATABLOCK')
        definition_valid = False
    else:
        sep = block_definition['SEPARATOR'][0]
        if sep not in supported_separators:
            print('WARNING: unsupported separator' + block_definition['SEPARATOR'])
            definition_valid = False
        else: 
            if sep == '"~':
                split_id = '~'
            if sep == '"\\t':
                split_id = '\t'
            if sep == '"=':
                split_id = '='
            verified_definition['SEPARATOR'] = split_id

    # verify the dimensions
    dimlist = []
    nr_rows = 0
    nr_columns = 0
    if definition_valid:
        if block_definition['DIM'] == None:
            print('WARNING: no dimensions found in DATABLOCK')
            # although no valid dimensions are found the data can still be valid
        else:
            dimlist = block_definition['DIM'][0].split('*')
            # assumed is here that:
            # - the cells of this list contain integers
            # - the length is 2
            # - the first entry contains the number of rows
            # - the second entry contains the number of columns
            if len(dimlist) == 2:
                nr_rows = int(dimlist[0])
                nr_columns = int(dimlist[1])
                verified_definition['DIM'] = [nr_rows, nr_columns]
            else:
                print('WARNING: the size of DIM list should be 2')


    if definition_valid:
        supported_types = ('FLOAT', 'INTEGER', 'STRING')
        if block_definition['TYPE'] == None:
            print('WARNING: no type found in DATABLOCK')
            # although no valid types are found the data can still be valid
        else:
            verified_type_list = []
            type_list = block_definition['TYPE']
            for t in type_list:
                if t not in supported_types:
                    print('WARNING ' + t + ' is not suported')
                    verified_type_list.append('UNSUPPORTED')
                else:
                    verified_type_list.append(t)

            verified_definition['TYPE'] = verified_type_list

    if definition_valid:
        if block_definition['NAME'] == None:  
            print('WARNING: no column names found in DATABLOCK')
            # although no valid types are found the data can still be valid
        else:
            verified_name_list = []
            name_list = block_definition['NAME']
            for n in name_list:
                verified_name_list.append(n)
                    
            verified_definition['NAME'] = verified_name_list

    # The DATABLOCK field is always present in the if no name is found a name 
    # is constructed from DATABLOCK and ID
    if definition_valid:
        if block_definition['GLOBAL'] == None:  
            print('WARNING: no global name found in DATABLOCK')
            verified_definition['GLOBAL'] = 'DATABLOCK' + block_definition['DATABLOCK'][0]
        else:
            verified_definition['GLOBAL'] = block_definition['GLOBAL'][0]


    return definition_valid, verified_definition

def convert_data_block( verified_definition, raw_data  ):

    # split the data into lists with lists    
    clean_row = []
    temp_data = []
    for row in raw_data:
    # strip the '\n' and split in
        clean_row = row.strip('\n').split(verified_definition['SEPARATOR'])
#        print(clean_row)
        # don't add empty rows
        if clean_row == ['']:
            print('empty row removed')
        else:
            temp_data.append(clean_row)
    
    # at this point the data from the block is present in a list of lists 
    # verify the data is valid
    if verify_block_data(temp_data):
        nr_rows = len(temp_data)
        nr_columns = len(temp_data[0])
        str_data = []
        temp_column = []
            
        # the data is organized in columns
        # the data in each column has the same type 
        # the column possibly has a name
        # rearrange thet data in columns
            
        for c in range(nr_columns):
            for r in range(nr_rows):
                temp_column.append(temp_data[r][c])
            str_data.append(temp_column.copy())
            temp_column.clear()
        # try to convert the data to floats
        float_data = []
        temp_float_array = []
        for c in range(nr_columns):
            for r in range(nr_rows):
                try:
                    #print(str_data[c][r])
                    temp_float_array.append(float(str_data[c][r]))
                except:
                    temp_float_array.append(None)
            float_data.append(temp_float_array.copy())
            temp_float_array.clear()
                
    else:
        print('ERROR: the data in this block is invalid')    


    # each of which contains the data in the form of strings 

    return str_data, float_data

def verify_block_data( data ):
    
    data_valid = True
    
    row_length = len(data[0])
    for row in data:
        if len(row) != row_length:
            print('ERROR: not all rows in raw_data have the same length')
            data_valid = False
    
    return data_valid
        
def read( filename ):
# function read
    # this function:
    # - reads all lines from a 'IBS' text file
    #
    # - split the lines into blocks. The 'DATABLOCK' string is used as 
    #   identifier for the start of each block. Each block contains the lines 
    #   from the line that contains 'DATABLOCK' till the last line before the
    #   next line that contains 'DATABLOCK'. The last block contains the lines
    #   from the last line that contains 'DATABLOCK' until the end of the file
    #
    # - find the block definition part and the data part in the lines for each 
    #   block. A 'blokdef' definition dict is returned that has the following 
    #   fields: 'DATABLOCK', 'GLOBAL', 'TYPE', 'NAME', 'SEPARATOR', 'DIM'
    #   When the field can be found in the definition part, the content of that 
    #   field is filled in as a list of strings. The raw data is a list of 
    #   strings of the the data part.
    #
    # - each block definition is verified. It should contain a valid 
    #   'SEPARATOR field. convert the raw data in string data and float data. 
    #   When all lines in the data part have the same number of entries the 
    #   raw data is converted into a 'stringdata'. Stringdata contains a list 
    #   of strings for each column in the data part of the block
    #   An attempt is made to conver the stingdata into floats. This is then 
    #   put in 'floatdata'. FLoat data contains lists of floating point values 
    #   for each column in the data block. If the conversion failed the entry
    #   contains 'None'
    #
    # - a list of dicts is returned turned. Each entry contains the fields:
    #   'BLOCKDEF'   will contain the verified definition if it is valid
    #                and the raw block defintion if it is invalid
    #   'RAWDATA'    will contain the lines of the block as they appear in the 
    #                input file
    #   'STRINGDATA' will contain the data in string format, if the definition 
    #                was valid
    #   'FLOATDATA'  will contain the data in floats, if the definition was 
    #                valid
    #
    lines = get_lines_from_file( filename )
    blocks = get_data_blocks(lines)
    
    ibs_dict = dict.fromkeys(('BLOCKDEF','RAWDATA','STRINGDATA','FLOATDATA'))
    ibs_content = []
    for block in blocks:
        blockdef, rawdata = read_data_block(block)
        ibs_dict['RAWDATA']  = rawdata

        definition_valid, verified_definition = verify_block_definition( blockdef )
        if definition_valid:
            strdata, floatdata = convert_data_block(verified_definition, rawdata)
            ibs_dict['BLOCKDEF'] = verified_definition
            ibs_dict['STRINGDATA'] = strdata
            ibs_dict['FLOATDATA'] = floatdata
        else:
            ibs_dict['BLOCKDEF'] = blockdef
            print('ERROR: can\'t covert block, definition is invalid')
        
        ibs_content.append(ibs_dict.copy())
        
    return ibs_content
#
#def convert( ibs_content ):
#    for element in ibs_content:
#        # verify the definition
#        print(ibs_content['BLOCKDEF'])
