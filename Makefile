AS=nasm
CC=gcc
LD=ld
CFLAGS=-m32 -ffreestanding -fno-pic -fno-pie -fno-stack-protector -nostdlib -nostartfiles -Wall -Wextra -O2
LDFLAGS=-m elf_i386 -T linker.ld -nostdlib
BUILD_DIR=build
BOOT_BIN=$(BUILD_DIR)/boot.bin
KERNEL_ELF=$(BUILD_DIR)/kernel.elf
KERNEL_BIN=$(BUILD_DIR)/kernel.bin
OS_IMAGE=os_image.img
KERNEL_OBJS=$(BUILD_DIR)/kernel.o $(BUILD_DIR)/graphics.o $(BUILD_DIR)/graphics_gui.o $(BUILD_DIR)/idt.o $(BUILD_DIR)/idt_asm.o $(BUILD_DIR)/timer.o $(BUILD_DIR)/keyboard.o $(BUILD_DIR)/mouse.o $(BUILD_DIR)/pci.o $(BUILD_DIR)/rtl8139.o $(BUILD_DIR)/task.o $(BUILD_DIR)/sys_call.o $(BUILD_DIR)/user_mode.o $(BUILD_DIR)/window.o $(BUILD_DIR)/luna_theme.o $(BUILD_DIR)/wm_events.o $(BUILD_DIR)/widgets.o $(BUILD_DIR)/desktop.o $(BUILD_DIR)/start_menu.o $(BUILD_DIR)/event_manager.o $(BUILD_DIR)/ramdisk.o $(BUILD_DIR)/fat.o $(BUILD_DIR)/elf.o $(BUILD_DIR)/net_stack.o $(BUILD_DIR)/protocols.o $(BUILD_DIR)/launcher.o $(BUILD_DIR)/app_notepad.o $(BUILD_DIR)/app_calc.o $(BUILD_DIR)/app_image_viewer.o $(BUILD_DIR)/app_minesweeper.o $(BUILD_DIR)/app_browser.o $(BUILD_DIR)/app_terminal.o $(BUILD_DIR)/app_settings.o $(BUILD_DIR)/xp_assets.o $(BUILD_DIR)/xp_layout_db.o $(BUILD_DIR)/local_db.o $(BUILD_DIR)/supabase_client.o $(BUILD_DIR)/app_ledger.o $(BUILD_DIR)/app_control_panel.o $(BUILD_DIR)/sys_env.o
.PHONY: all clean run
all: $(OS_IMAGE)
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)
$(BOOT_BIN): boot/boot.asm | $(BUILD_DIR)
	$(AS) -f bin $< -o $@
$(BUILD_DIR)/idt_asm.o: kernel/cpu/idt_asm.asm | $(BUILD_DIR)
	$(AS) -f elf32 $< -o $@
$(BUILD_DIR)/user_mode.o: kernel/multitasking/user_mode.asm | $(BUILD_DIR)
	$(AS) -f elf32 $< -o $@
$(BUILD_DIR)/kernel.o: kernel/kernel.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/graphics.o: kernel/graphics.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/graphics_gui.o: kernel/graphics_gui.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/idt.o: kernel/cpu/idt.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/timer.o: kernel/drivers/timer.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/keyboard.o: kernel/drivers/keyboard.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/mouse.o: kernel/drivers/mouse.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/pci.o: kernel/drivers/pci.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/rtl8139.o: kernel/drivers/rtl8139.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/task.o: kernel/multitasking/task.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/sys_call.o: kernel/multitasking/sys_call.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/window.o: kernel/gui/window.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/luna_theme.o: kernel/gui/luna_theme.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/wm_events.o: kernel/gui/wm_events.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/widgets.o: kernel/gui/widgets.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/desktop.o: kernel/gui/desktop.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/start_menu.o: kernel/gui/start_menu.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/event_manager.o: kernel/gui/event_manager.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/ramdisk.o: kernel/storage/ramdisk.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/fat.o: kernel/fs/fat.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/elf.o: kernel/loader/elf.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/net_stack.o: kernel/net/net_stack.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/protocols.o: kernel/net/protocols.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/launcher.o: kernel/apps/launcher.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/app_notepad.o: apps/notepad.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/app_calc.o: apps/calc.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/app_image_viewer.o: apps/image_viewer.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/app_minesweeper.o: apps/minesweeper.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/app_browser.o $(BUILD_DIR)/app_terminal.o $(BUILD_DIR)/app_settings.o $(BUILD_DIR)/xp_assets.o $(BUILD_DIR)/xp_layout_db.o $(BUILD_DIR)/local_db.o $(BUILD_DIR)/supabase_client.o $(BUILD_DIR)/app_ledger.o $(BUILD_DIR)/app_control_panel.o $(BUILD_DIR)/sys_env.o: apps/browser.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(KERNEL_ELF): $(KERNEL_OBJS) linker.ld
	$(LD) $(LDFLAGS) -o $@ $(KERNEL_OBJS)
$(KERNEL_BIN): $(KERNEL_ELF)
	objcopy -O binary $< $@
$(OS_IMAGE): $(BOOT_BIN) $(KERNEL_BIN)
	cat $(BOOT_BIN) $(KERNEL_BIN) > $(OS_IMAGE)
	truncate -s 1474560 $(OS_IMAGE)
run: $(OS_IMAGE)
	qemu-system-i386 -drive format=raw,file=$(OS_IMAGE) -net nic,model=rtl8139 -net user
clean:
	rm -rf $(BUILD_DIR) $(OS_IMAGE)

$(BUILD_DIR)/app_terminal.o: apps/terminal.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/app_settings.o: apps/settings.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD_DIR)/xp_assets.o: kernel/gui/xp_assets.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/xp_layout_db.o: kernel/gui/xp_layout_db.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD_DIR)/local_db.o: kernel/db/local_db.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/supabase_client.o: kernel/net/supabase_client.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/app_ledger.o $(BUILD_DIR)/app_control_panel.o $(BUILD_DIR)/sys_env.o: apps/ledger_app.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD_DIR)/app_control_panel.o: apps/control_panel.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
$(BUILD_DIR)/sys_env.o: kernel/config/sys_env.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@
