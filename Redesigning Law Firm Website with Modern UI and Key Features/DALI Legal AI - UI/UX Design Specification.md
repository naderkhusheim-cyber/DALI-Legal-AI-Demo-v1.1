# DALI Legal AI - UI/UX Design Specification

This document outlines the user interface (UI) and user experience (UX) design specifications for key features of the DALI Legal AI platform. It details the visual elements, interaction flows, and design principles applied to ensure a modern, intuitive, and efficient experience for legal professionals.

## 1. Login and Register Pages

### 1.1. Login Page

**Purpose**: To provide a secure and visually appealing entry point for users to access the DALI Legal AI platform.

**Layout & Visuals**:
-   **Two-Tone Background**: The page features a split background, with a dark, gradient-filled section on the left (for larger screens) and a lighter, clean section on the right for the login form.
    -   *Left Section (Branding)*: Displays the DALI Legal AI logo, name, and a compelling tagline. It also highlights key benefits of the platform with icons and descriptive text, encouraging user engagement. A subtle background pattern adds depth without distraction.
    -   *Right Section (Form)*: A clean, minimalist white background ensures focus on the login form.
-   **Branding**: The DALI Legal AI logo (brain icon with text) is prominently displayed on both sections, maintaining brand consistency.
-   **Responsive Design**: The left branding section collapses on smaller screens, prioritizing the login form for mobile users.

**Elements & Interactions**:
-   **Email/Password Fields**: Standard input fields with clear labels and placeholder text. Password field includes a toggle to show/hide password for user convenience.
-   **


### 1.2. Register Page

**Purpose**: To allow new users to create an account and join the DALI Legal AI platform.

**Layout & Visuals**:
-   **Consistent Branding**: Mirrors the Login page's two-tone background and branding elements, providing a cohesive user experience.
-   **Form-Centric Design**: The right section is dedicated to the registration form, ensuring all necessary fields are clearly presented.

**Elements & Interactions**:
-   **Multi-Field Form**: Includes fields for First Name, Last Name, Email Address, Phone Number, Company/Law Firm, Password, and Confirm Password.
-   **Password Visibility Toggle**: Similar to the Login page, password fields have an eye icon to toggle visibility.
-   **Terms & Privacy Checkboxes**: Users must agree to Terms of Service and Privacy Policy, with clickable links to these documents. An optional newsletter subscription checkbox is also provided.
-   **


### 1.3. Social Sign-On (SSO)
-   **Providers**: Google and Apple SSO options are provided for quick and convenient registration/login.
-   **Placement**: Clearly visible buttons below the traditional email/password login/registration fields.

## 2. Contract Management Page

**Purpose**: To provide a centralized hub for users to manage, track, and analyze all their legal contracts.

**Layout & Visuals**:
-   **Dashboard Layout**: A clean, organized dashboard with a clear overview of contracts.
-   **Search and Filter**: Prominent search bar and filter options for easy contract discovery.
-   **Contract List**: Displays contracts in a card or list format, showing key information like client, type, value, dates, and risk level.
-   **Overview Section**: Quick statistics on total value, active contracts, expiring contracts, and average risk level.
-   **Templates Section**: Showcases pre-built contract templates for quick access.
-   **Recent Activity**: A timeline of recent actions related to contracts.

**Elements & Interactions**:
-   **"New Contract" Button**: A prominent button that triggers the `NewContractModal` (described below).
-   **Search Bar**: Allows users to search by contract name, client, or type.
-   **Filter Options**: Buttons to filter contracts by status (All, Active, Pending, Draft, Expired) and a "More Filters" option for advanced filtering.
-   **Contract Cards**: Each card provides a summary of a contract, including status, client, type, value, dates, completion progress, and risk level. Actions like View, Edit, Duplicate, and Export are available.
-   **Contract Templates**: Displays available templates with a "Use" button to initiate the drafting process.
-   **Quick Actions**: Buttons for common tasks like "Create Contract", "Import Contracts", and "Archive Old Contracts".

## 3. New Contract Modal

**Purpose**: To guide users through the initial selection process for creating a new contract, offering various types and sub-types.

**Layout & Visuals**:
-   **Modal Overlay**: Appears as a central overlay, dimming the background content, ensuring focus.
-   **Two-Step Process**: Clearly guides the user through selecting a contract type and then a sub-type.
-   **Contract Type Selection**: Displays 8 main contract categories (Corporate, Employment, Real Estate, Commercial, Banking & Finance, Intellectual Property, Family & Personal Status, International) as visually distinct cards.
    -   Each card includes an icon, name, brief description, and the number of available templates.
    -   Color-coded icons enhance visual appeal and differentiation.
-   **Sub-Type Selection**: After selecting a main type, a list of specific sub-types is presented.
    -   Each sub-type card includes an icon, name, description, estimated setup time, jurisdiction (Saudi Law), and AI-assisted indicator.

**Elements & Interactions**:
-   **Contract Type Cards**: Clickable cards that transition to the sub-type selection step.
-   **Sub-Type Cards**: Clickable cards that, upon selection, close the modal and navigate the user to the `ContractDrafting` page, passing the selected contract details.
-   **Back Button**: Allows users to return from sub-type selection to main type selection.
-   **Cancel Button**: Closes the modal at any step.
-   **Hover Effects**: Cards provide visual feedback on hover, indicating interactivity.

## 4. AI-Assisted Contract Drafting Interface

**Purpose**: To provide an interactive environment where users can draft contracts with real-time AI assistance and a live document preview.

**Layout & Visuals**:
-   **Split-Screen Layout**: The primary interface is divided into two main sections:
    -   **Left Panel (AI Chat)**: Dedicated to interaction with the AI legal assistant.
    -   **Right Panel (Contract Preview)**: Displays the live, editable contract document.
-   **Header**: Displays the selected contract type and sub-type for context.

**Elements & Interactions (Left Panel - AI Chat)**:
-   **AI Assistant**: A chat interface for natural language interaction with the AI.
-   **Input Field**: Text input area for typing commands or questions to the AI.
-   **Voice Input**: Microphone icon for voice-to-text input, with a visual indicator for recording status.
-   **File Attachment**: Paperclip icon to attach relevant documents for AI analysis or inclusion.
-   **Message History**: Displays the conversation flow between the user and the AI, with timestamps.
-   **Smart Responses**: AI provides contextual responses, suggestions, and asks clarifying questions to guide the drafting process.

**Elements & Interactions (Right Panel - Contract Preview)**:
-   **Live Document Editor**: The contract content updates in real-time based on AI interactions and user input.
-   **Header Elements**: Customizable areas at the top of the document:
    -   **Company Logo**: Upload or select a logo to be placed at the top.
    -   **Contract Title**: Dynamically updated based on AI drafting or user input.
    -   **Effective Date**: Input field for the contract's effective date.
-   **Watermark**: Option to add a customizable watermark (e.g., 


    "DRAFT", "CONFIDENTIAL") in the middle of the document.
-   **Signature Blocks**: Clearly defined areas for all parties to sign, including fields for printed names, titles, and dates.
-   **Editable Fields**: Specific sections or clauses within the contract can be directly edited by the user in the preview pane.

**Multilingual Support**:
-   **Language Detection**: The AI detects the language of user input (Arabic, English, or both).
-   **Single Language Output**: If input is purely Arabic or English, the contract is drafted in that single language.
-   **Bilingual Output**: If input contains both Arabic and English, the contract is generated with parallel Arabic (right-aligned) and English (left-aligned) text for each clause, ensuring comprehensive coverage for bilingual legal contexts.

**Action Buttons**:
-   **Save**: Saves the current state of the contract.
-   **Export**: Exports the contract in various formats (e.g., PDF, Word).
-   **Share**: Allows sharing the contract with other team members or external parties.
-   **Print**: Prints the contract directly from the interface.

This concludes the detailed UI/UX Design Specification for the requested features. This document can serve as a reference for further development and design iterations.

