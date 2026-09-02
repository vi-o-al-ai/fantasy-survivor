variable "name" {
  description = "Base name for the bucket and distribution."
  type        = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
