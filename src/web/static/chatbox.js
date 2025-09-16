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
    let flashingUserId = null;
    let flashingInterval = null;

    // ========== USER SEARCH BAR ==========
    const userSearchDiv = document.createElement('div');
    userSearchDiv.style.display = 'flex';
    userSearchDiv.style.flexDirection = 'column';
    userSearchDiv.style.marginLeft = '10px';
    userSearchDiv.style.width = '70%';
    userSearchDiv.style.position = 'relative';

    const userSearchInput = document.createElement('input');
    userSearchInput.type = 'text';
    userSearchInput.placeholder = 'Search users...';
    userSearchInput.style.marginBottom = '4px';
    userSearchInput.style.padding = '4px';
    userSearchInput.style.borderRadius = '6px';
    userSearchInput.style.border = '1px solid #ccc';

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

    userSearchDiv.appendChild(userDropdown);
    userSearchDiv.appendChild(userSearchInput);
    chatboxHeader.appendChild(userSearchDiv);

    let dropdownIndex = -1;
    function renderUserDropdown() {
        userDropdown.innerHTML = '';
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
            item.style.color = '#111';
            item.addEventListener('mousedown', function(e) {
                e.preventDefault();
                selectUser(u.id);
            });
            userDropdown.appendChild(item);
        });
        userDropdown.style.display = 'block';
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
        fetch('/api/users/search?q=' + encodeURIComponent(q))
            .then(r => r.json())
            .then(data => {
                users = data.users || [];
                dropdownIndex = -1;
                renderUserDropdown();
            });
    }

    // ========== USER LIST ==========
    function renderUserList() {
        chatboxMessages.innerHTML = '';
        users.forEach((u) => {
            const userDiv = document.createElement('div');
            userDiv.className = 'chatbox-user-list-item';
            userDiv.style.display = 'flex';
            userDiv.style.alignItems = 'center';
            userDiv.style.padding = '10px 8px';
            userDiv.style.cursor = 'pointer';
            userDiv.style.borderBottom = '1px solid #f0f0f0';
            userDiv.style.transition = 'background 0.3s';
            userDiv.dataset.userid = u.id;

            // Flashing effect
            if (u.id === flashingUserId) {
                userDiv.classList.add('flashing-user');
            } else {
                userDiv.classList.remove('flashing-user');
            }

            // Status dot
            const statusDot = document.createElement('span');
            statusDot.style.display = 'inline-block';
            statusDot.style.width = '10px';
            statusDot.style.height = '10px';
            statusDot.style.borderRadius = '50%';
            statusDot.style.marginRight = '10px';
            statusDot.style.background = u.online ? '#27ae60' : '#bbb';
            userDiv.appendChild(statusDot);

            // Username
            const usernameSpan = document.createElement('span');
            usernameSpan.textContent = u.username;
            userDiv.appendChild(usernameSpan);

            userDiv.addEventListener('click', function() {
                selectUser(u.id);
            });
            chatboxMessages.appendChild(userDiv);
        });
    }

    function startFlashing(userId) {
        flashingUserId = userId;
        if (flashingInterval) clearInterval(flashingInterval);
        flashingInterval = setInterval(() => {
            const userDivs = document.querySelectorAll('.chatbox-user-list-item');
            userDivs.forEach(div => {
                if (parseInt(div.dataset.userid) === userId) {
                    div.style.background = div.style.background === 'rgb(102, 174, 238)' ? '#fff' : '#66aeee';
                }
            });
        }, 1000);
    }

    function stopFlashing() {
        if (flashingInterval) clearInterval(flashingInterval);
        flashingUserId = null;
        const userDivs = document.querySelectorAll('.chatbox-user-list-item');
        userDivs.forEach(div => {
            div.style.background = '#fff';
        });
    }

    function fetchAllUsers(callback) {
        fetch('/api/users/all')
            .then(r => r.json())
            .then(data => {
                users = data.users || [];
                renderUserList();
                if (callback) callback();
            });
    }

    function showUserList() {
        selectedUserId = null;
        stopFlashing();
        fetchAllUsers();
    }

    // ========== CHATBOX TOGGLE ==========
    if (chatboxToggle) {
        chatboxToggle.addEventListener('click', function() {
            chatboxContainer.style.display = 'flex';
            chatboxToggle.style.display = 'none';
            showUserList(); // Always show list first
            fetch('/api/chat/mark_read', { method: 'POST' });
            updateUnreadBadge(0);
        });
    }
    if (chatboxClose) {
        chatboxClose.addEventListener('click', function() {
            chatboxContainer.style.display = 'none';
            chatboxToggle.style.display = 'flex';
            if (chatPollInterval) clearInterval(chatPollInterval);
            showUserList();
        });
    }

    // ========== CHAT ACTIONS ==========
    function fetchChatHistory() {
        if (!selectedUserId) return;
        
        // Store current scroll position
        const currentScrollTop = chatboxMessages.scrollTop;
        const isAtBottom = Math.abs(chatboxMessages.scrollHeight - chatboxMessages.clientHeight - currentScrollTop) < 5;
        
        fetch(`/api/chat/history?with_user=${selectedUserId}`)
            .then(r => r.json())
            .then(data => {
                chatboxMessages.innerHTML = '';
                if (data.messages && data.messages.length > 0) {
                    data.messages.forEach(msg => {
                        const isYou = msg.sender_id == window.CURRENT_USER_ID;
                        const senderName = isYou ? 'You' : getUsernameById(msg.sender_id);
                        appendMessage(senderName, msg.message, isYou);
                    });
                } else {
                    const noMsgDiv = document.createElement('div');
                    noMsgDiv.textContent = 'No messages yet. Start the conversation!';
                    noMsgDiv.style.textAlign = 'center';
                    noMsgDiv.style.color = '#888';
                    noMsgDiv.style.padding = '20px';
                    chatboxMessages.appendChild(noMsgDiv);
                }
                
                // Only scroll to bottom if user was at bottom, otherwise maintain position
                if (isAtBottom) {
                    chatboxMessages.scrollTop = chatboxMessages.scrollHeight;
                }
            })
            .catch(error => {
                console.error('Error fetching chat history:', error);
            });
    }

    function selectUser(userId) {
        selectedUserId = userId;
        stopFlashing();
        fetchChatHistory();
        if (chatPollInterval) clearInterval(chatPollInterval);
        if (selectedUserId) {
            chatPollInterval = setInterval(fetchChatHistory, 2000);
        }
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

    // ========== INCOMING MESSAGE POLL ==========
    setInterval(() => {
        if (!selectedUserId && chatboxContainer.style.display === 'flex') {
            fetch('/api/chat/last_message')
                .then(r => r.json())
                .then(data => {
                    if (data.new_message) {
                        const senderId = data.new_message.sender_id;
                        const idx = users.findIndex(u => u.id === senderId);
                        if (idx > 0) {
                            const user = users.splice(idx, 1)[0];
                            users.unshift(user);
                        }
                        renderUserList();
                        startFlashing(senderId);
                    }
                });
        }
    }, 3000);

    // ========== NOTIFICATIONS ==========
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
            fetch('/api/chat/unread_count')
                .then(r => r.json())
                .then(data => {
                    updateUnreadBadge(data.unread || 0);
                });
        } else {
            updateUnreadBadge(0);
        }
    }, 3000);

    function getUsernameById(id) {
        const u = users.find(u => u.id == id);
        return u ? u.username : 'User';
    }

    window.CURRENT_USER_ID = window.CURRENT_USER_ID || null;
    
    // Update user activity every 30 seconds
    setInterval(() => {
        fetch('/api/user/update_activity', { method: 'POST' })
            .catch(error => console.error('Error updating activity:', error));
    }, 30000);
    
    showUserList(); // Show list on page load
});
