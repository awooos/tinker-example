; asmsyntax=nasm

global _start               ; Make entrypoint visible to linker.
global stack_bottom         ; Bottom of the stack.
global stack_top            ; Top of the stack.
extern hal_store_magic      ; Defined in hal/magic.c.
extern tinker_kernel_main   ; Defined in src/kernel.c.

; Amount of space to reserve for the stack.
STACKSIZE equ 0x4000        ; That's 16KB.

; Multiboot header. See GRUB documentation for details.
; https://www.gnu.org/software/grub/manual/multiboot2/multiboot.html
MODULEALIGN equ  1<<0            ; Align modules on page boundaries.
MEMINFO     equ  1<<1            ; Provide memory map.
FLAGS       equ  MODULEALIGN | MEMINFO  ; Multiboot flag field.
MAGIC       equ  0x1BADB002      ; Magic number so bootloader can find the header.
CHECKSUM    equ -(MAGIC + FLAGS) ; Checksum required.

; Executable section.
section .text
  align 4
  MultiBootHeader:
      dd MAGIC
      dd FLAGS
      dd CHECKSUM

  _start:
    mov  esp, stack_top     ; Set up the stack.
    push ebx                ; Argument to kernel_main.
    push eax                ; Provided by Multiboot-compliant bootloaders.

    call hal_store_magic    ; Store magic numbers and such!
    mov  esp, stack_top     ; Reset the stack since we don't care about the
                            ; contents anymore.

    call tinker_kernel_main ; Call kernel proper.

    ; We only get here if the kernel returns.
    ; This, generally speaking, probably shouldn't happen.

    cli                     ; Stop interrupts.
    hlt                     ; Halt the machine.


; Data section.
section .bss
  stack_bottom:

  align 32
  resb STACKSIZE    ; Reserve stack on a quadword boundary.

  stack_top:

