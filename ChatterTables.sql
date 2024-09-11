-- Tables
CREATE TABLE Users
(
    user_id BIGSERIAL NOT NULL PRIMARY KEY, 
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    user_created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_details_updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Chats
(
    chat_id BIGSERIAL NOT NULL PRIMARY KEY,
    chat_name VARCHAR(50) NOT NULL,
    chat_created_at TIMESTAMP NOT NULL,
    chat_owner_id BIGINT REFERENCES Users (user_id) NOT NULL,
    chat_details_updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Participants
(
    PRIMARY KEY (chat_id, user_id),
    chat_id BIGINT REFERENCES Chats (chat_id),
    user_id BIGINT REFERENCES Users (user_id)
);

CREATE TABLE Messages
(
    message_id BIGSERIAL NOT NULL PRIMARY KEY,
    sender_id BIGINT REFERENCES Users (user_id),
    message_sent_at TIMESTAMP NOT NULL,
    chat_id BIGINT REFERENCES Chats (chat_id),
    message_content VARCHAR(256) NOT NULL
);


-- Participants Table Indexes
CREATE INDEX participant ON Participants(chat_id, user_id);

-- Messages Table Indexes
CREATE INDEX chat_id_index ON Messages(chat_id);

-- Chats Table Indexes
CREATE INDEX chat_owner_id ON Chats(chat_owner_id);
