package build_gate
import rego.v1

# 1. กฎเหล็ก: Default Deny เสมอ (ห้ามลืม!)
default allow := false

# 2. อนุญาตก็ต่อเมื่อ "ไม่มี deny" และ "มีไฟล์"
allow if {
    count(deny) == 0
    count(input.files) > 0
}

# 3. ตรวจสอบว่ามีไฟล์ส่งมาจริงไหม
deny contains "AST evidence contains no files" if {
    count(input.files) == 0
}

# 4. ตรวจสอบ SHA256 (Format ต้องถูกต้อง)
deny contains sprintf("Invalid SHA256 checksum for file: %s", [file.path]) if {
    some file in input.files
    not regex.match(`^[0-9a-f]{64}$`, file.sha256)
}

# 5. [NEW] ตรวจสอบว่า AST Parser ทำงานสำเร็จหรือไม่
deny contains sprintf("AST parsing failed for file: %s", [file.path]) if {
    some file in input.files
    file.ast.parse_ok != true
}

# 6. [NEW] ป้องกัน Path Traversal หรือ Path ว่างเปล่า
deny contains sprintf("Suspicious or empty file path detected: %v", [file]) if {
    some file in input.files
    not file.path
    # หรือถ้าอยากเช็ก Path Traversal ให้ใช้: contains(file.path, "..")
}
