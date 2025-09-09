document.addEventListener('DOMContentLoaded', function() {
    const chatboxToggle = document.getElementById('chatbox-toggle');
    const chatboxContainer = document.getElementById('chatbox-container');
    const chatboxClose = document.getElementById('chatbox-close');
    const chatboxInput = document.getElementById('chatbox-input-field');
    const chatboxSend = document.getElementById('chatbox-send');
    const chatboxMessages = document.getElementById('chatbox-messages');
    const chatboxHeader = document.getElementById('chatbox-header');

    let selectedUserId = null;
    let users = [];
    let chatPollInterval = null;

    // Add user search bar and selection dropdown
    const userSearchDiv = document.createElement('div');
    userSearchDiv.style.display = 'flex';
    userSearchDiv.style.flexDirection = 'column';
    userSearchDiv.style.marginLeft = '10px';
    userSearchDiv.style.width = '70%';
    const userSearchInput = document.createElement('input');
    userSearchInput.type = 'text';
    userSearchInput.placeholder = 'Search users...';
    userSearchInput.style.marginBottom = '4px';
    userSearchInput.style.padding = '4px';
    userSearchInput.style.borderRadius = '6px';
    userSearchInput.style.border = '1px solid #ccc';
    // Replace <select> with custom dropdown
    const userDropdown = document.createElement('div');
    userDropdown.id = 'chatbox-user-dropdown';
    userDropdown.style.position = 'absolute';
    userDropdown.style.top = '38px';
    userDropdown.style.left = '0';
    userDropdown.style.right = '0';
    userDropdown.style.background = '#fff';
    userDropdown.style.border = '1px solid #ccc';
    userDropdown.style.borderRadius = '6px';
    userDropdown.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
    userDropdown.style.zIndex = '1002';
    userDropdown.style.display = 'none';
    userDropdown.style.maxHeight = '180px';
    userDropdown.style.overflowY = 'auto';
    userDropdown.style.cursor = 'pointer';
    userSearchDiv.style.position = 'relative';
    userSearchDiv.appendChild(userDropdown);
    // Remove <select> from DOM
    // userSearchDiv.removeChild(userSelect); // This line is removed as per the new_code

    userSearchDiv.appendChild(userSearchInput);
    chatboxHeader.appendChild(userSearchDiv);

    let dropdownIndex = -1;
    function renderUserDropdown() {
        userDropdown.innerHTML = '';
        // Only show 'No users found' if the user has typed something
        if (users.length === 0) {
            if (userSearchInput.value.trim().length > 0) {
                const noUser = document.createElement('div');
                noUser.textContent = 'No users found';
                noUser.style.padding = '8px 12px';
                noUser.style.color = '#888';
                userDropdown.appendChild(noUser);
                userDropdown.style.display = 'block';
            } else {
                userDropdown.style.display = 'none';
            }
            return;
        }
        users.forEach((u, idx) => {
            const item = document.createElement('div');
            item.textContent = u.username;
            item.style.padding = '8px 12px';
            item.style.borderBottom = '1px solid #f0f0f0';
            item.style.background = idx === dropdownIndex ? '#e3eaf2' : '#fff';
            item.style.color = '#111'; // Always black for visibility
            item.addEventListener('mousedown', function(e) {
                e.preventDefault();
                selectUser(u.id);
            });
            userDropdown.appendChild(item);
        });
        userDropdown.style.display = 'block';
    }
    function selectUser(userId) {
        selectedUserId = userId;
        userSearchInput.value = users.find(u => u.id == userId).username;
        userDropdown.style.display = 'none';
        fetchChatHistory();
        if (chatPollInterval) clearInterval(chatPollInterval);
        if (selectedUserId) {
            chatPollInterval = setInterval(fetchChatHistory, 2000);
        }
    }
    userSearchInput.addEventListener('input', function() {
        fetchUsers(this.value);
    });
    userSearchInput.addEventListener('focus', function() {
        fetchUsers(this.value);
    });
    userSearchInput.addEventListener('blur', function() {
        setTimeout(() => { userDropdown.style.display = 'none'; }, 200);
    });
    userSearchInput.addEventListener('keydown', function(e) {
        if (userDropdown.style.display === 'block') {
            if (e.key === 'ArrowDown') {
                dropdownIndex = Math.min(dropdownIndex + 1, users.length - 1);
                renderUserDropdown();
                e.preventDefault();
            } else if (e.key === 'ArrowUp') {
                dropdownIndex = Math.max(dropdownIndex - 1, 0);
                renderUserDropdown();
                e.preventDefault();
            } else if (e.key === 'Enter' && dropdownIndex >= 0) {
                selectUser(users[dropdownIndex].id);
                e.preventDefault();
            }
        }
    });

    function fetchUsers(q = "") {
        fetch('/api/users/search?q=' + encodeURIComponent(q)).then(r => r.json()).then(data => {
            users = data.users || [];
            dropdownIndex = -1;
            renderUserDropdown();
        });
    }

    function fetchChatHistory() {
        if (selectedUserId) {
            fetch(`/api/chat/history?with_user=${selectedUserId}`)
                .then(r => r.json())
                .then(data => {
                    chatboxMessages.innerHTML = '';
                    (data.messages || []).forEach(msg => {
                        appendMessage(msg.sender_id === window.CURRENT_USER_ID ? 'You' : getUsernameById(msg.sender_id), msg.message, msg.sender_id === window.CURRENT_USER_ID);
                    });
                });
        }
    }

    // Show all users by default when search is empty
    // userSearchInput.addEventListener('focus', function() {
    //     if (!this.value) fetchUsers("");
    //     userSelect.size = userSelect.options.length;
    // });
    // userSearchInput.addEventListener('blur', function() {
    //     setTimeout(() => { userSelect.size = 1; }, 200);
    // });
    // userSearchInput.addEventListener('input', function() {
    //     fetchUsers(this.value);
    //     userSelect.size = userSelect.options.length;
    // });

    // userSelect.addEventListener('change', function() {
    //     selectedUserId = this.value;
    //     fetchChatHistory();
    //     if (chatPollInterval) clearInterval(chatPollInterval);
    //     if (selectedUserId) {
    //         chatPollInterval = setInterval(fetchChatHistory, 2000);
    //     }
    // });

    function getUsernameById(id) {
        const u = users.find(u => u.id == id);
        return u ? u.username : 'User';
    }

    // Notification badge logic
    let unreadBadge = null;
    function updateUnreadBadge(count) {
        if (!unreadBadge) {
            unreadBadge = document.createElement('div');
            unreadBadge.style.position = 'absolute';
            unreadBadge.style.top = '-8px';
            unreadBadge.style.right = '-8px';
            unreadBadge.style.background = '#e74c3c';
            unreadBadge.style.color = '#fff';
            unreadBadge.style.borderRadius = '50%';
            unreadBadge.style.width = '22px';
            unreadBadge.style.height = '22px';
            unreadBadge.style.display = 'flex';
            unreadBadge.style.alignItems = 'center';
            unreadBadge.style.justifyContent = 'center';
            unreadBadge.style.fontSize = '0.95rem';
            unreadBadge.style.fontWeight = 'bold';
            unreadBadge.style.zIndex = '10000';
            unreadBadge.style.pointerEvents = 'none';
            unreadBadge.id = 'chatbox-unread-badge';
            var wrapper = document.getElementById('chatbox-toggle-wrapper');
            if (wrapper) {
                wrapper.style.position = 'fixed';
                wrapper.appendChild(unreadBadge);
            }
        }
        unreadBadge.textContent = count;
        unreadBadge.style.display = count > 0 ? 'flex' : 'none';
    }
    let unreadPollInterval = setInterval(function() {
        if (chatboxContainer.style.display === 'none') {
            fetch('/api/chat/unread_count').then(r => r.json()).then(data => {
                updateUnreadBadge(data.unread || 0);
            });
        } else {
            updateUnreadBadge(0);
        }
    }, 3000);
    if (chatboxToggle) {
        chatboxToggle.addEventListener('click', function() {
            chatboxContainer.style.display = 'flex';
            chatboxToggle.style.display = 'none';
            fetchUsers(userSearchInput.value);
            // Mark as read
            fetch('/api/chat/mark_read', { method: 'POST' });
            updateUnreadBadge(0);
        });
    }
    if (chatboxClose) {
        chatboxClose.addEventListener('click', function() {
            chatboxContainer.style.display = 'none';
            chatboxToggle.style.display = 'flex';
            if (chatPollInterval) clearInterval(chatPollInterval);
        });
    }
    if (chatboxInput) {
        chatboxInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                chatboxSend.click();
            }
        });
    }
    if (chatboxSend) {
        chatboxSend.addEventListener('click', function() {
            const message = chatboxInput.value.trim();
            if (message && selectedUserId) {
                fetch('/api/chat/send', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message, receiver_id: selectedUserId })
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        appendMessage('You', message, true);
                        chatboxInput.value = '';
                        setTimeout(() => chatboxInput.focus(), 100);
                        fetchChatHistory();
                    }
                });
            }
        });
    }
    function appendMessage(sender, text, isYou) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'chatbox-message' + (isYou ? ' you' : '');
        msgDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
        chatboxMessages.appendChild(msgDiv);
        chatboxMessages.scrollTop = chatboxMessages.scrollHeight;
    }

    // Add Share from Knowledge Base button
    const shareKbBtn = document.createElement('button');
    shareKbBtn.textContent = 'Share from Knowledge Base';
    shareKbBtn.style.margin = '8px 0 0 0';
    shareKbBtn.style.padding = '6px 12px';
    shareKbBtn.style.borderRadius = '6px';
    shareKbBtn.style.background = '#667eea';
    shareKbBtn.style.color = '#fff';
    shareKbBtn.style.border = 'none';
    shareKbBtn.style.cursor = 'pointer';
    shareKbBtn.style.fontWeight = 'bold';
    shareKbBtn.style.width = '100%';
    chatboxHeader.appendChild(shareKbBtn);

    let kbModal = null;
    shareKbBtn.addEventListener('click', function() {
        if (!selectedUserId) {
            alert('Select a user to share with first.');
            return;
        }
        fetch('/api/knowledge-base/my-documents').then(r => r.json()).then(data => {
            const docs = data.documents || [];
            if (kbModal) kbModal.remove();
            kbModal = document.createElement('div');
            kbModal.style.position = 'fixed';
            kbModal.style.top = '50%';
            kbModal.style.left = '50%';
            kbModal.style.transform = 'translate(-50%, -50%)';
            kbModal.style.background = '#fff';
            kbModal.style.border = '1px solid #ccc';
            kbModal.style.borderRadius = '10px';
            kbModal.style.boxShadow = '0 4px 16px rgba(0,0,0,0.15)';
            kbModal.style.zIndex = '2000';
            kbModal.style.padding = '24px';
            kbModal.style.minWidth = '320px';
            kbModal.innerHTML = '<h3>Select a document to share</h3>';
            const select = document.createElement('select');
            select.style.width = '100%';
            select.style.marginBottom = '12px';
            docs.forEach(doc => {
                const opt = document.createElement('option');
                opt.value = doc.id;
                opt.textContent = `${doc.title} (${doc.document_type})`;
                select.appendChild(opt);
            });
            kbModal.appendChild(select);
            const shareBtn = document.createElement('button');
            shareBtn.textContent = 'Share Document';
            shareBtn.style.background = '#10a37f';
            shareBtn.style.color = '#fff';
            shareBtn.style.border = 'none';
            shareBtn.style.borderRadius = '6px';
            shareBtn.style.padding = '8px 16px';
            shareBtn.style.fontWeight = 'bold';
            shareBtn.style.marginRight = '8px';
            kbModal.appendChild(shareBtn);
            const cancelBtn = document.createElement('button');
            cancelBtn.textContent = 'Cancel';
            cancelBtn.style.background = '#eee';
            cancelBtn.style.color = '#333';
            cancelBtn.style.border = 'none';
            cancelBtn.style.borderRadius = '6px';
            cancelBtn.style.padding = '8px 16px';
            kbModal.appendChild(cancelBtn);
            document.body.appendChild(kbModal);
            cancelBtn.addEventListener('click', function() {
                kbModal.remove();
            });
            shareBtn.addEventListener('click', function() {
                const docId = select.value;
                fetch('/api/knowledge-base/share', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ doc_id: docId, receiver_id: selectedUserId })
                }).then(r => r.json()).then(data => {
                    if (data.success) {
                        alert('Document shared!');
                        kbModal.remove();
                        fetchChatHistory();
                    } else {
                        alert('Failed to share document.');
                    }
                });
            });
        });
    });

    // Expose current user ID for message sender check
    window.CURRENT_USER_ID = window.CURRENT_USER_ID || null;
});
