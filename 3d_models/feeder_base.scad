// Automated Cat Feeder - Main Base Enclosure
// OpenSCAD file for 3D printing

// Parameters
base_width = 200;
base_depth = 150;
base_height = 80;
wall_thickness = 2;
pi_width = 85;
pi_depth = 56;
pi_height = 15;

// Raspberry Pi 4 dimensions
pi_mount_holes = [
    [3.5, 3.5],
    [3.5, 61.5],
    [61.5, 3.5],
    [61.5, 61.5]
];

// GPIO header position
gpio_x = 21;
gpio_y = 3.5;
gpio_width = 51;
gpio_depth = 5;

// USB ports position
usb_x = 0;
usb_y = 6;
usb_width = 15;
usb_height = 8;

// Power port position
power_x = 70;
power_y = 6;
power_width = 8;
power_height = 8;

// Ventilation holes
vent_diameter = 3;
vent_spacing = 15;

module main_base() {
    difference() {
        // Main base
        cube([base_width, base_depth, base_height]);
        
        // Internal cavity
        translate([wall_thickness, wall_thickness, wall_thickness])
        cube([base_width - 2*wall_thickness, base_depth - 2*wall_thickness, base_height - wall_thickness]);
        
        // Pi mounting area
        translate([(base_width - pi_width)/2, (base_depth - pi_depth)/2, wall_thickness])
        cube([pi_width, pi_depth, pi_height + 5]);
        
        // Pi mounting holes
        translate([(base_width - pi_width)/2, (base_depth - pi_depth)/2, 0])
        for (hole = pi_mount_holes) {
            translate([hole[0], hole[1], -1])
            cylinder(h = wall_thickness + 2, d = 3, $fn = 20);
        }
        
        // GPIO access hole
        translate([(base_width - pi_width)/2 + gpio_x, (base_depth - pi_depth)/2 + gpio_y, wall_thickness])
        cube([gpio_width, gpio_depth, pi_height + 5]);
        
        // USB ports access
        translate([(base_width - pi_width)/2 + usb_x, (base_depth - pi_depth)/2 + usb_y, wall_thickness])
        cube([usb_width, usb_depth, usb_height]);
        
        // Power port access
        translate([(base_width - pi_width)/2 + power_x, (base_depth - pi_depth)/2 + power_y, wall_thickness])
        cube([power_width, power_depth, power_height]);
        
        // Ventilation holes - top
        for (x = [vent_spacing : vent_spacing : base_width - vent_spacing]) {
            for (y = [vent_spacing : vent_spacing : base_depth - vent_spacing]) {
                translate([x, y, base_height - wall_thickness - 1])
                cylinder(h = wall_thickness + 2, d = vent_diameter, $fn = 20);
            }
        }
        
        // Ventilation holes - sides
        for (y = [vent_spacing : vent_spacing : base_depth - vent_spacing]) {
            // Left side
            translate([wall_thickness - 1, y, base_height/2])
            rotate([0, 90, 0])
            cylinder(h = wall_thickness + 2, d = vent_diameter, $fn = 20);
            
            // Right side
            translate([base_width - wall_thickness + 1, y, base_height/2])
            rotate([0, -90, 0])
            cylinder(h = wall_thickness + 2, d = vent_diameter, $fn = 20);
        }
        
        // Cable management holes
        // Power cable
        translate([base_width/2, base_depth - wall_thickness - 1, base_height/2])
        rotate([90, 0, 0])
        cylinder(h = wall_thickness + 2, d = 8, $fn = 20);
        
        // Sensor cables
        translate([base_width - wall_thickness - 1, base_depth/2, base_height/2])
        rotate([0, -90, 0])
        cylinder(h = wall_thickness + 2, d = 6, $fn = 20);
    }
}

module mounting_brackets() {
    // Front mounting bracket
    translate([0, -10, 0])
    cube([base_width, 10, wall_thickness]);
    
    // Back mounting bracket
    translate([0, base_depth, 0])
    cube([base_width, 10, wall_thickness]);
    
    // Mounting holes
    for (x = [20, base_width - 20]) {
        // Front holes
        translate([x, -5, wall_thickness/2])
        rotate([90, 0, 0])
        cylinder(h = 15, d = 4, $fn = 20);
        
        // Back holes
        translate([x, base_depth + 5, wall_thickness/2])
        rotate([-90, 0, 0])
        cylinder(h = 15, d = 4, $fn = 20);
    }
}

module lcd_mount() {
    lcd_width = 80;
    lcd_height = 36;
    lcd_depth = 12;
    
    translate([(base_width - lcd_width)/2, base_depth - lcd_depth - 10, base_height - lcd_height - 10])
    difference() {
        cube([lcd_width, lcd_depth, lcd_height]);
        
        // LCD cutout
        translate([2, 2, 2])
        cube([lcd_width - 4, lcd_depth - 4, lcd_height - 4]);
        
        // Mounting holes
        translate([10, lcd_depth/2, lcd_height/2])
        rotate([0, 90, 0])
        cylinder(h = lcd_depth + 2, d = 3, $fn = 20);
        
        translate([lcd_width - 10, lcd_depth/2, lcd_height/2])
        rotate([0, -90, 0])
        cylinder(h = lcd_depth + 2, d = 3, $fn = 20);
    }
}

module button_panel() {
    button_width = 15;
    button_height = 15;
    button_depth = 5;
    
    translate([10, base_depth - 30, base_height - 25])
    difference() {
        cube([base_width - 20, 20, 15]);
        
        // Button holes
        for (i = [0:3]) {
            translate([20 + i*25, 10, 5])
            cylinder(h = button_depth + 2, d = button_width, $fn = 20);
        }
        
        // LED hole
        translate([base_width - 40, 10, 5])
        cylinder(h = button_depth + 2, d = 5, $fn = 20);
    }
}

// Main assembly
main_base();
mounting_brackets();
lcd_mount();
button_panel(); 