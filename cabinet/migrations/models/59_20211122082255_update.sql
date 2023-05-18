-- upgrade --
ALTER TABLE "booking_booking" RENAME COLUMN "ddu_approved" TO "ddu_accepted";
-- downgrade --
ALTER TABLE "booking_booking" RENAME COLUMN "ddu_accepted" TO "ddu_approved";
