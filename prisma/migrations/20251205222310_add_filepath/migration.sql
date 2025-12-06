-- AlterTable
ALTER TABLE "KnowledgeDocument" ADD COLUMN     "filePath" TEXT;

-- CreateTable
CREATE TABLE "ChatSession" (
    "id" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    "userId" TEXT NOT NULL,
    "title" TEXT NOT NULL DEFAULT 'New Chat',
    "messages" JSONB NOT NULL,

    CONSTRAINT "ChatSession_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "_ChatSessionToKnowledgeDocument" (
    "A" TEXT NOT NULL,
    "B" TEXT NOT NULL
);

-- CreateIndex
CREATE INDEX "ChatSession_userId_idx" ON "ChatSession"("userId");

-- CreateIndex
CREATE INDEX "ChatSession_createdAt_idx" ON "ChatSession"("createdAt");

-- CreateIndex
CREATE UNIQUE INDEX "_ChatSessionToKnowledgeDocument_AB_unique" ON "_ChatSessionToKnowledgeDocument"("A", "B");

-- CreateIndex
CREATE INDEX "_ChatSessionToKnowledgeDocument_B_index" ON "_ChatSessionToKnowledgeDocument"("B");
