-- 創建數據庫
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'GameLauncher')
BEGIN
    CREATE DATABASE GameLauncher;
END
GO

USE GameLauncher;
GO

-- 創建用戶表
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Users')
BEGIN
    CREATE TABLE Users (
        UserID INT IDENTITY(1,1) PRIMARY KEY,
        Username NVARCHAR(50) NOT NULL UNIQUE,
        Password NVARCHAR(100) NOT NULL,
        Email NVARCHAR(100) NOT NULL UNIQUE,
        CreatedAt DATETIME NOT NULL,
        Points INT NOT NULL DEFAULT 0,
        LastLogin DATETIME NULL
    );
END
GO

-- 創建登入歷史表
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'LoginHistory')
BEGIN
    CREATE TABLE LoginHistory (
        LoginID INT IDENTITY(1,1) PRIMARY KEY,
        UserID INT NOT NULL,
        LoginTime DATETIME NOT NULL,
        IPAddress NVARCHAR(50) NOT NULL,
        FOREIGN KEY (UserID) REFERENCES Users(UserID)
    );
END
GO

-- 創建交易歷史表
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TransactionHistory')
BEGIN
    CREATE TABLE TransactionHistory (
        TransactionID INT IDENTITY(1,1) PRIMARY KEY,
        UserID INT NOT NULL,
        PointsChange INT NOT NULL,
        Reason NVARCHAR(200) NOT NULL,
        TransactionTime DATETIME NOT NULL,
        FOREIGN KEY (UserID) REFERENCES Users(UserID)
    );
END
GO

-- 創建成就表
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Achievements')
BEGIN
    CREATE TABLE Achievements (
        AchievementID INT IDENTITY(1,1) PRIMARY KEY,
        Name NVARCHAR(100) NOT NULL,
        Description NVARCHAR(500) NOT NULL,
        Points INT NOT NULL,
        IconPath NVARCHAR(200) NULL
    );
END
GO

-- 創建用戶成就表
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'UserAchievements')
BEGIN
    CREATE TABLE UserAchievements (
        UserAchievementID INT IDENTITY(1,1) PRIMARY KEY,
        UserID INT NOT NULL,
        AchievementID INT NOT NULL,
        UnlockedAt DATETIME NOT NULL,
        FOREIGN KEY (UserID) REFERENCES Users(UserID),
        FOREIGN KEY (AchievementID) REFERENCES Achievements(AchievementID)
    );
END
GO

-- 創建虛擬物品表
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'VirtualItems')
BEGIN
    CREATE TABLE VirtualItems (
        ItemID INT IDENTITY(1,1) PRIMARY KEY,
        Name NVARCHAR(100) NOT NULL,
        Description NVARCHAR(500) NOT NULL,
        Price INT NOT NULL,
        IconPath NVARCHAR(200) NULL,
        IsAvailable BIT NOT NULL DEFAULT 1
    );
END
GO

-- 創建用戶物品表
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'UserItems')
BEGIN
    CREATE TABLE UserItems (
        UserItemID INT IDENTITY(1,1) PRIMARY KEY,
        UserID INT NOT NULL,
        ItemID INT NOT NULL,
        PurchaseTime DATETIME NOT NULL,
        IsUsed BIT NOT NULL DEFAULT 0,
        FOREIGN KEY (UserID) REFERENCES Users(UserID),
        FOREIGN KEY (ItemID) REFERENCES VirtualItems(ItemID)
    );
END
GO

-- 創建遊戲表
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Games')
BEGIN
    CREATE TABLE Games (
        GameID INT IDENTITY(1,1) PRIMARY KEY,
        Name NVARCHAR(100) NOT NULL,
        Description NVARCHAR(500) NOT NULL,
        Version NVARCHAR(50) NOT NULL,
        ExecutablePath NVARCHAR(200) NOT NULL,
        IconPath NVARCHAR(200) NULL,
        IsAvailable BIT NOT NULL DEFAULT 1
    );
END
GO

-- 創建更新歷史表
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'UpdateHistory')
BEGIN
    CREATE TABLE UpdateHistory (
        UpdateID INT IDENTITY(1,1) PRIMARY KEY,
        GameID INT NOT NULL,
        Version NVARCHAR(50) NOT NULL,
        UpdateTime DATETIME NOT NULL,
        Description NVARCHAR(500) NOT NULL,
        FOREIGN KEY (GameID) REFERENCES Games(GameID)
    );
END
GO

-- 插入一些測試數據
-- 插入測試用戶
IF NOT EXISTS (SELECT * FROM Users WHERE Username = 'test')
BEGIN
    INSERT INTO Users (Username, Password, Email, CreatedAt, Points)
    VALUES ('test', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBAQNQxJxJ5K8y', 'test@example.com', GETDATE(), 1000);
END
GO

-- 插入測試成就
IF NOT EXISTS (SELECT * FROM Achievements)
BEGIN
    INSERT INTO Achievements (Name, Description, Points, IconPath)
    VALUES 
    ('初次登入', '完成首次登入', 10, 'icons/first_login.png'),
    ('積分達人', '累計獲得1000積分', 50, 'icons/points_master.png'),
    ('購物狂', '購買10個虛擬物品', 30, 'icons/shopaholic.png');
END
GO

-- 插入測試虛擬物品
IF NOT EXISTS (SELECT * FROM VirtualItems)
BEGIN
    INSERT INTO VirtualItems (Name, Description, Price, IconPath)
    VALUES 
    ('VIP會員', '獲得VIP特權30天', 500, 'icons/vip.png'),
    ('幸運符', '增加遊戲幸運值', 100, 'icons/lucky_charm.png'),
    ('經驗加倍', '遊戲經驗值加倍24小時', 200, 'icons/exp_boost.png');
END
GO

-- 插入測試遊戲
IF NOT EXISTS (SELECT * FROM Games)
BEGIN
    INSERT INTO Games (Name, Description, Version, ExecutablePath, IconPath)
    VALUES 
    ('幸運輪盤', '經典賭場遊戲', '1.0.0', 'games/lucky_wheel.exe', 'icons/lucky_wheel.png'),
    ('21點', '經典撲克遊戲', '1.0.0', 'games/blackjack.exe', 'icons/blackjack.png'),
    ('老虎機', '經典賭場遊戲', '1.0.0', 'games/slot_machine.exe', 'icons/slot_machine.png');
END
GO 