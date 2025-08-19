# Overview

This repository contains a comprehensive Telegram bot built in Python with multiple advanced features including API analysis, vulnerability scanning, website cloning, user session management, mass reporting capabilities, and external database login search. The bot is designed for cybersecurity research, OSINT (Open Source Intelligence) operations, and automated Telegram interactions with robust logging and configuration management.

## Recent Changes (August 19, 2025)

### System Updates - v6.0 COMPLETE OVERHAUL (Latest Session)
- **COMPLETE V6 CLEANUP FINISHED** - Comprehensive reorganization and code cleanup completed
- **PROMOTIONAL CONTENT REMOVED** - All divulgacao/promotional systems completely removed
- **INVALID COMMAND HANDLING REMOVED** - Removed annoying command suggestion system for cleaner UX  
- **ORBI SEARCH API REMOVAL** - Completely removed all Orbi Search functionality as requested
- **NEW URL SEARCH API INTEGRATION** - Added http://147.79.86.21:5019/search?term= API for /url command  
- **IMPROVED LOGIN SEARCH RESPONSE HANDLING** - Enhanced logins_search.py with better error handling, duplicate prevention, and quality validation
- **CALLBACK HANDLER UPDATES** - Updated format1_orbi/format2_orbi to format1_url/format2_url handlers
- **DIAGNOSTIC SYSTEM UPDATED** - Replaced Orbi diagnostic tests with new external API connectivity tests
- **CLEAN ORGANIZED STRUCTURE** - All functions, systems, and buttons properly organized and tested
- **IMPROVED ERROR HANDLING** - Better error management throughout all systems
- **ADDED USER REQUESTED BUTTONS** - Added "🔑 Adquirir APIs" (https://xpldata.com) and "👤 Contatar Dono" (https://t.me/inatuavel) buttons to /start menu
- **COMPREHENSIVE ADMIN PANEL IMPLEMENTED** - Added complete admin panel for DONO_ID (7210984282) with user management, statistics, tools, and backup features
- **ADMIN COMMAND SUITE ADDED** - Implemented /stats, /listusers, /botinfo, /backup, /autorizar, /desautorizar, and broadcast commands
- **LSP ERROR FIXES** - Fixed critical import errors, undefined variables, and type checking issues
- **DYNAMIC BUTTON SYSTEM** - Admin panel button appears only for the identified admin user (7210984282)
- **COMPLETE V6.0 OVERHAUL FINISHED** - All requested changes implemented and bot fully operational

### Previous Updates

**MIGRATION TO REPLIT ENVIRONMENT COMPLETED**
- ✅ Successfully migrated from Replit Agent to native Replit environment
- ✅ All dependencies installed and configured properly 
- ✅ Database systems initialized successfully
- ✅ Telegram bot connected and operational
- ✅ All major features verified and working
- ✅ Security practices maintained during migration
- ✅ Project structure optimized for Replit compatibility

- **COMPLETE MENU REORGANIZATION** - Removed confusing `/comandos` system and implemented 6 separate themed menus
- **NEW MENU STRUCTURE**: 
  - `/logins` - Login search tools (buscar, url, search)
  - `/reports` - Reporting systems (report, reportwpp)
  - `/geradores` - Data generation tools
  - `/scraper` - Web extraction tools
  - `/security` - Security analysis tools
  - `/checkers` - Verification tools
- **Enhanced User Experience** - Each menu has dedicated buttons and navigation with "Back to Start" functionality
- **Session Configuration Fixed** - Resolved Telegram session conflicts and authorization issues
- **NEW: External Login Search System** - Added `/buscar [termo]` command that searches an external API database for login credentials
- **File Generation System** - Implemented automatic TXT file generation with user:pass and url:user:pass formats
- **Cache Management** - Added user-specific result caching for seamless file format selection
- **ORBI SEARCH COMPLETELY FIXED** - Now uses REAL orbi-space.shop API:
  - **Fixed API URLs**: Now connects to correct orbi-space.shop endpoints found in codebase
  - **Real API Integration**: Uses actual API format: base=clouds&token=teste&query={domain}
  - **Authentic Results Only**: Completely removed fake data generation (200k-500k fake results)
  - **Accurate Counting**: Shows only real credentials found from API responses
  - **Multiple Endpoints**: Tests various orbi-space.shop API endpoints with different formats
  - **Enhanced Error Handling**: Proper connection timeouts and response validation
- **AUTHORIZATION SYSTEM IMPROVEMENTS**:
  - Removed authorization check from /start command (now works for everyone)
  - Added group support - bot works in groups without individual ID verification
  - Enhanced command recognition system to include all menu commands
  - Fixed "command not recognized" issues with comprehensive command list
- **FILE NAMING ENHANCEMENTS**:
  - Added search term/URL to generated file names for better organization
  - Files now named as: {user_id}_orbi_{clean_query}.txt
  - Improved file pattern matching for download functionality

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Bot Framework
- **Telethon-based Architecture**: Uses Telethon library for advanced Telegram API interactions, allowing for more sophisticated bot operations beyond basic message handling
- **Dual Bot Configuration**: Supports both simple telegram-bot integration and advanced Telethon client functionality
- **Modular Handler System**: Separate handlers.py module for command processing and message handling with comprehensive error handling and logging

## Database & Session Management  
- **SQLite Database**: Local SQLite database for storing collected user sessions, account information, and reporting statistics
- **Session Collection System**: Advanced system for collecting and managing multiple Telegram user sessions from public groups
- **Mass Reporting Infrastructure**: Coordinated reporting system using multiple accounts with configurable report reasons and rate limiting

## Security & Analysis Components
- **API Discovery Engine**: Comprehensive API analysis tool that scans websites for REST endpoints, GraphQL, WebSocket connections, and API documentation
- **Vulnerability Scanner**: Professional-grade vulnerability assessment tool scanning for SQL injection, XSS, CSRF, exposed files, and security misconfigurations
- **Website Cloning System**: Advanced web scraping and cloning capabilities with concurrent downloading, asset discovery, and bypass mechanisms

## Search & Intelligence Systems
- **Multi-source Login Search**: Integration with external APIs for credential discovery and breach data analysis
- **Orbi Space Integration**: Specialized search engine integration for enhanced data collection
- **Premium Reporting**: Advanced PDF/image report generation with professional formatting and data visualization

## Configuration & Logging
- **Environment-based Configuration**: Secure configuration management using environment variables and .env files
- **Comprehensive Logging**: Multi-level logging system with file rotation, console output, and structured log formatting
- **Flexible Message Templates**: Centralized message configuration for consistent bot responses

# External Dependencies

## Core Libraries
- **Telethon**: Primary Telegram client library for advanced API interactions
- **python-telegram-bot**: Secondary bot framework for basic command handling
- **Requests & urllib3**: HTTP client libraries with SSL configuration and connection pooling
- **BeautifulSoup4**: HTML parsing for web scraping and content extraction
- **Pillow (PIL)**: Image processing library for report generation and visual content creation

## Database & Storage
- **SQLite3**: Local database for session management and data persistence
- **python-dotenv**: Environment variable management for secure configuration

## Specialized Tools
- **SSEClient**: Server-Sent Events client for real-time data streaming from external APIs
- **concurrent.futures**: Parallel processing for web scraping and vulnerability scanning
- **hashlib**: Cryptographic functions for data integrity and user identification

## External Services
- **Telegram API**: Core messaging platform integration requiring API_ID, API_HASH, and BOT_TOKEN
- **Custom API Endpoints**: Integration with external services like "patronhost.online" and "orbi-space.shop" for specialized data collection
- **Web Target Analysis**: Dynamic analysis of user-provided websites and APIs without predefined service dependencies