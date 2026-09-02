variable "name" {
  description = "Table name."
  type        = string
}

variable "point_in_time_recovery" {
  description = "Enable PITR backups (recommended for prod)."
  type        = bool
  default     = false
}

variable "tags" {
  type    = map(string)
  default = {}
}
