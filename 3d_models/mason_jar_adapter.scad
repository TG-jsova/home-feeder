// Automated Cat Feeder - Mason Jar Adapter
// OpenSCAD file for 3D printing
// Replaces custom hopper with standard mason jar support

// Mason jar thread specifications (Wide Mouth)
jar_thread_diameter = 86.0;  // mm (3.4 inches)
jar_thread_pitch = 2.5;      // mm per thread
jar_thread_height = 8.0;     // mm thread engagement
jar_neck_diameter = 70.0;    // mm neck diameter

// Adapter parameters
adapter_height = 50;         // mm total height
adapter_wall_thickness = 3;  // mm
adapter_flange_height = 8;   // mm mounting flange

// Servo mounting
servo_width = 22.2;
servo_depth = 11.8;
servo_height = 31;
servo_mount_thickness = 3;

// Food outlet
outlet_diameter = 25;        // mm

// Base mounting (matches feeder base)
base_width = 200;
base_depth = 150;

module mason_jar_threads() {
    // Internal threads for mason jar
    difference() {
        // Main thread cylinder
        cylinder(h = jar_thread_height, d = jar_thread_diameter, $fn = 60);
        
        // Thread cutouts
        for (i = [0 : jar_thread_pitch : jar_thread_height]) {
            translate([0, 0, i])
            difference() {
                cylinder(h = jar_thread_pitch, d = jar_thread_diameter + 2, $fn = 60);
                cylinder(h = jar_thread_pitch, d = jar_thread_diameter - 2, $fn = 60);
            }
        }
    }
}

module main_adapter() {
    difference() {
        // Main adapter body
        cylinder(h = adapter_height, d = jar_thread_diameter + 2*adapter_wall_thickness, $fn = 60);
        
        // Internal cavity
        translate([0, 0, adapter_flange_height])
        cylinder(h = adapter_height - adapter_flange_height, d = jar_thread_diameter, $fn = 60);
        
        // Mason jar threads
        translate([0, 0, adapter_flange_height])
        mason_jar_threads();
        
        // Food outlet at bottom
        translate([0, 0, -1])
        cylinder(h = adapter_flange_height + 2, d = outlet_diameter, $fn = 40);
        
        // Servo mounting cutout
        translate([-servo_width/2, -servo_depth/2, adapter_flange_height - servo_height])
        cube([servo_width, servo_depth, servo_height + 1]);
        
        // Ventilation holes around top
        for (angle = [0 : 30 : 330]) {
            rotate([0, 0, angle])
            translate([jar_thread_diameter/2 - 5, 0, adapter_height - 5])
            cylinder(h = 6, d = 4, $fn = 20);
        }
    }
}

module mounting_flange() {
    flange_width = base_width - 20;  // Slightly smaller than base
    flange_depth = base_depth - 20;
    
    translate([-flange_width/2, -flange_depth/2, 0])
    difference() {
        cube([flange_width, flange_depth, adapter_flange_height]);
        
        // Mounting holes (4 corners)
        for (x = [15, flange_width - 15]) {
            for (y = [15, flange_depth - 15]) {
                translate([x, y, -1])
                cylinder(h = adapter_flange_height + 2, d = 4, $fn = 20);
            }
        }
        
        // Center cutout for adapter
        translate([flange_width/2 - jar_thread_diameter/2 - adapter_wall_thickness, 
                   flange_depth/2 - jar_thread_diameter/2 - adapter_wall_thickness, -1])
        cube([jar_thread_diameter + 2*adapter_wall_thickness, 
              jar_thread_diameter + 2*adapter_wall_thickness, 
              adapter_flange_height + 2]);
    }
}

module servo_mount() {
    // Servo mounting bracket
    translate([-servo_width/2 - 5, -servo_depth/2 - 5, adapter_flange_height - servo_height - servo_mount_thickness])
    difference() {
        cube([servo_width + 10, servo_depth + 10, servo_mount_thickness]);
        
        // Servo mounting holes
        translate([5, 5, -1])
        cylinder(h = servo_mount_thickness + 2, d = 3, $fn = 20);
        
        translate([servo_width + 5, 5, -1])
        cylinder(h = servo_mount_thickness + 2, d = 3, $fn = 20);
        
        translate([5, servo_depth + 5, -1])
        cylinder(h = servo_mount_thickness + 2, d = 3, $fn = 20);
        
        translate([servo_width + 5, servo_depth + 5, -1])
        cylinder(h = servo_mount_thickness + 2, d = 3, $fn = 20);
        
        // Servo body cutout
        translate([5, 5, -1])
        cube([servo_width, servo_depth, servo_mount_thickness + 2]);
    }
}

module food_gate() {
    gate_width = outlet_diameter + 10;
    gate_height = 8;
    gate_depth = 3;
    
    // Gate arm
    translate([-gate_width/2, -gate_depth/2, adapter_flange_height - gate_height])
    difference() {
        cube([gate_width, gate_depth, gate_height]);
        
        // Servo arm attachment hole
        translate([gate_width/2, gate_depth/2, gate_height/2])
        rotate([90, 0, 0])
        cylinder(h = gate_depth + 2, d = 2, $fn = 20);
    }
}

module jar_support_ring() {
    // Support ring for jar bottom (optional)
    ring_diameter = jar_thread_diameter + 10;
    ring_height = 5;
    
    translate([0, 0, adapter_height])
    difference() {
        cylinder(h = ring_height, d = ring_diameter, $fn = 60);
        cylinder(h = ring_height, d = jar_thread_diameter - 5, $fn = 60);
    }
}

// Main assembly
main_adapter();
mounting_flange();
servo_mount();
food_gate();

// Uncomment to add jar support ring
// jar_support_ring();

// Optional: Add a mason jar for visualization
module mason_jar() {
    jar_height = 150;
    jar_body_diameter = 95;
    
    color([0.8, 0.8, 0.8])  // Light gray for glass
    translate([0, 0, adapter_height])
    difference() {
        // Jar body
        cylinder(h = jar_height, d = jar_body_diameter, $fn = 60);
        
        // Jar cavity
        translate([0, 0, 5])
        cylinder(h = jar_height - 5, d = jar_body_diameter - 4, $fn = 60);
        
        // Threaded neck
        translate([0, 0, jar_height - jar_thread_height])
        cylinder(h = jar_thread_height, d = jar_thread_diameter, $fn = 60);
    }
}

// Uncomment to visualize with mason jar
// mason_jar(); 