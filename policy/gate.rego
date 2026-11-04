package build_gate
import rego.v1

deny contains "AST evidence contains no files" if {
    count(input.files) == 0
}

deny contains sprintf("Invalid SHA256 checksum for file: %s", [file.path]) if {
    some file in input.files
    not regex.match(`^[0-9a-f]{64}$`, file.sha256)
}
