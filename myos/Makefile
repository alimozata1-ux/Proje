CC=i686-elf-gcc
LD=i686-elf-ld
AS=nasm

CFLAGS=-ffreestanding -m32 -nostdlib -nostdinc -fno-builtin -fno-stack-protector -Wall -Wextra -Iinclude
LDFLAGS=-T linker.ld -nostdlib

BUILD_DIR=build
KERNEL_BIN=$(BUILD_DIR)/kernel.bin

KERNEL_OBJS= \
	$(BUILD_DIR)/kernel_entry.o \
	$(BUILD_DIR)/kernel.o \
	$(BUILD_DIR)/vga.o \
	$(BUILD_DIR)/keyboard.o \
	$(BUILD_DIR)/task.o \
	$(BUILD_DIR)/scheduler.o \
	$(BUILD_DIR)/paging.o \
	$(BUILD_DIR)/allocator.o \
	$(BUILD_DIR)/syscall.o \
	$(BUILD_DIR)/user.o \
	$(BUILD_DIR)/io.o \
	$(BUILD_DIR)/memory.o \
	$(BUILD_DIR)/string.o \
	$(BUILD_DIR)/serial.o \
	$(BUILD_DIR)/logger.o \
	$(BUILD_DIR)/panic.o \
	$(BUILD_DIR)/keyboard_buffer.o \
	$(BUILD_DIR)/shell.o \
	$(BUILD_DIR)/gui.o \
	$(BUILD_DIR)/browser.o \
	$(BUILD_DIR)/settings.o \
	$(BUILD_DIR)/notifications.o \
	$(BUILD_DIR)/driver.o \
	$(BUILD_DIR)/syscall_table.o \
	$(BUILD_DIR)/diagnostics.o \
	$(BUILD_DIR)/fs.o \
	$(BUILD_DIR)/system_apps.o

all: os.img

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BUILD_DIR)/boot.bin: boot/boot.asm | $(BUILD_DIR)
	$(AS) -f bin $< -o $@

$(BUILD_DIR)/kernel_entry.o: kernel/kernel_entry.asm | $(BUILD_DIR)
	$(AS) -f elf32 $< -o $@

$(BUILD_DIR)/%.o: kernel/%.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(KERNEL_BIN): $(KERNEL_OBJS) linker.ld
	$(LD) $(LDFLAGS) -o $@ $(KERNEL_OBJS)

os.img: $(BUILD_DIR)/boot.bin $(KERNEL_BIN)
	cat $(BUILD_DIR)/boot.bin $(KERNEL_BIN) > $@

run: os.img
	qemu-system-i386 -drive format=raw,file=os.img

clean:
	rm -rf $(BUILD_DIR) os.img

.PHONY: all run clean
