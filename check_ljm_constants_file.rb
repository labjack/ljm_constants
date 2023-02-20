#!/usr/bin/env ruby

# Name: check_ljm_constants_file.rb
# Desc: Prints out the things that might be wrong with the ljm_constants.json file

require 'rubygems'
# This is needed on CentOS 32-bit build machine for whatever reason

require 'pathname'
require 'json'

CUR_DIR = Pathname(__FILE__).dirname.realpath
LJM_HEADER = "#{CUR_DIR}/../header_files/api/LabJackM.h"
CONSTANTS_FILE = "#{CUR_DIR}/../../ljm_constants/LabJack/LJM/ljm_constants.json"
IGNORE_FILE = "error_codes_to_ignore.txt"

# Error patterns
LJM_ERROR_PATTERN = /LJM_ERROR_CODE\s*(\w+)\s*[=]\s*(\d+)\s*;/

RANGED_REGISTER_NAME_PATTERN = /[a-zA-Z]+\w*#\(\d+:\d+\)\w*/

def get_ignore_error_array (file)
  ignore_array = []
  ignorefile = File.read(IGNORE_FILE)
  ignorefile.each_line do |ignorename|
    ignorename.tr!("\r\n", "")
    ignore_array.push(ignorename)
  end
  return ignore_array

end

# Add errors to error_array
def add_errors_header_file (file, pattern, error_array)
  ignore_array = get_ignore_error_array(IGNORE_FILE)
  lines = File.read(file)
  lines.gsub! /\/\*![^*]*\*+(?:[^*\/][^*]*\*+)*\//, '' # Remove multi-line comments
  lines.gsub! /\/\/.*$/, '' # Remove single-line comments
  lines.each_line do |line|
    line.scan(pattern) do |errorname,errorcode|
      # puts line if DEBUG
      if ! errorname.start_with?("LJME_")
        puts "Weird errorname: #{errorname}. line: #{line}"
      end
      error_array << Array[errorcode, errorname] unless ((errorcode.to_i == 0) || (ignore_array.include? errorname))
    end
  end
end

def add_errors_from_json_file (file, error_array)
  lines = File.read(file)
  json = JSON.parse(lines)
  abort("no errors element found the the JSON file") unless json.has_key? 'errors'

  json["errors"].each do |errorline|
    abort("errorline #{errorline} has no string element") unless errorline.has_key? 'string'
    errorname = errorline["string"]
    abort("errorline #{errorline} has no error element") unless errorline.has_key? 'error'
    errorcode = errorline["error"]
    error_array << Array[errorcode, errorname] if errorname.start_with?("LJME_")
  end
end

def estr(err)
  return "#{err[0]} - #{err[1]}"
end

# Compares only the first to the second (call this function twice with the arrays swapped)
def compare_error_arrays(file_name, array_a, array_b)
  err_strs = []
  array_a.each do |a|
    found = false
    array_b.each do |b|
      found = true if a[0].to_i == b[0].to_i && a[1] == b[1]
      err_strs << "errorcode match, but not error name: #{estr(a)} (b is #{estr(b)})" if !found and a[0].to_i == b[0].to_i
      err_strs << "error name match, but not errorcode: #{estr(a)} (b is #{estr(b)})" if !found and a[1] == b[1]
    end
    err_strs << "unmatched: #{estr(a)}" unless found
  end
  puts "#{err_strs.size} errorcode match errors/warnings in #{file_name}" if err_strs.size != 0
  err_strs.each do |str|
    puts "    #{str}"
  end
end


def check_ljm_error_codes_against_constants_file()
  header_errors = []
  constant_file_errors = []

  add_errors_header_file(LJM_HEADER, LJM_ERROR_PATTERN, header_errors)
  add_errors_from_json_file(CONSTANTS_FILE, constant_file_errors)

  compare_error_arrays(LJM_HEADER, header_errors, constant_file_errors)
  compare_error_arrays(CONSTANTS_FILE, constant_file_errors, header_errors)
end

# Para: regs - json registers
def check_register_names_for_spaces(regs)
  regs.each do |reg|
    abort("register has no name: #{reg}") unless reg.has_key? 'name'
    name = reg["name"]
    if (name.include? " ")
      puts "Register has a space in name: #{name}"
    end
  end
end

def check_register_names_for_valid_range_notation(regs)
  regs.each do |reg|
    name = reg["name"]
    if (name.include? "#")
      if !RANGED_REGISTER_NAME_PATTERN.match(name)
        puts "Register name has invalid range notation: #{name}"
      end
    end
  end
end

def check_ljm_constants_ok()
  lines = File.read(CONSTANTS_FILE)
  json = JSON.parse(lines)

  register_name_check = ["registers", "registers_beta"]
  register_name_check.each do |reg_set_name|
    check_register_names_for_spaces(json[reg_set_name])
    check_register_names_for_valid_range_notation(json[reg_set_name])
  end

end



#######################################################
# Begin                                               #
#######################################################

check_ljm_error_codes_against_constants_file()
check_ljm_constants_ok()

exit
