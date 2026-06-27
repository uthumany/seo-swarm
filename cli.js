#!/usr/bin/env node
/**
 * SEO SWARM - Autonomous SEO Swarm Agents CLI
 * Node.js entry point that delegates to the Python CLI.
 * @author uthuman Inc
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Banner
console.log('\x1b[96m\x1b[1m');
console.log('   ╔══════════════════════════════════════════════════════════════╗');
console.log('   ║     ███████╗███████╗ ██████╗     ███████╗██╗    ██╗ █████╗ ██████╗ ███╗   ███╗   ║');
console.log('   ║     ██╔════╝██╔════╝██╔═══██╗    ██╔════╝██║    ██║██╔══██╗██╔══██╗████╗ ████║   ║');
console.log('   ║     ███████╗█████╗  ██║   ██║    ███████╗██║ █╗ ██║███████║██████╔╝██╔████╔██║   ║');
console.log('   ║     ╚════██║██╔══╝  ██║   ██║    ╚════██║██║███╗██║██╔══██║██╔══██╗██║╚██╔╝██║   ║');
console.log('   ║     ███████║███████╗╚██████╔╝    ███████║╚███╔███╔╝██║  ██║██║  ██║██║ ╚═╝ ██║   ║');
console.log('   ║     ╚══════╝╚══════╝ ╚═════╝     ╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝   ║');
console.log('   ║                                                                              ║');
console.log('   ║     \x1b[93m🐝 °°°°°●°°°°°●°°°●°°° > SEO SWARM\x1b[96m     ║');
console.log('   ║     \x1b[90mAutonomous Multi-Agent SEO Automation Platform v1.0.0\x1b[96m          ║');
console.log('   ╚══════════════════════════════════════════════════════════════════════════════╝');
console.log('\x1b[0m\n');

// Check for Python
const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
const cliPath = path.join(__dirname, 'src', 'seo_swarm', 'cli.py');

if (!fs.existsSync(cliPath)) {
  console.log('\x1b[91mERROR: CLI module not found. Please run: pip install seo-swarm\x1b[0m');
  process.exit(1);
}

// Pass all args to Python CLI
const args = process.argv.slice(2);
const child = spawn(pythonCmd, [cliPath, ...args], {
  stdio: 'inherit',
  env: { ...process.env, PYTHONUNBUFFERED: '1' }
});

child.on('error', (err) => {
  console.log(`\x1b[91mError: Python not found. Install Python 3.8+ and run: pip install seo-swarm\x1b[0m`);
  process.exit(1);
});

child.on('close', (code) => {
  process.exit(code || 0);
});
