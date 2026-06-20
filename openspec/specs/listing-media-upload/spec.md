# Listing Media Upload Specification

## Purpose
Defines backend-mediated listing image upload and display behavior.

## Requirements

### Requirement: Backend-Mediated Listing Image Upload
The system SHALL allow listing images to be uploaded through backend-controlled endpoints and SHALL NOT require users to paste image URLs for listing media.

#### Scenario: Farmer uploads image for own listing
- **WHEN** an authenticated Farmer uploads a valid image file for a listing they own
- **THEN** the backend SHALL validate the file, store it using the configured storage adapter, persist the resulting image URL, and attach it to the listing

#### Scenario: Upload without configured storage
- **WHEN** listing image upload is requested but Cloudinary or an approved local development fallback is not configured
- **THEN** the backend SHALL return a controlled configuration error without storing fake image URLs

### Requirement: Cloudinary Secret Isolation
The system SHALL use Cloudinary only from the backend when `CLOUDINARY_URL` is configured and SHALL NOT expose Cloudinary API secrets to frontend environment variables or browser code.

#### Scenario: Frontend uploads through backend
- **WHEN** a user uploads a listing image from the frontend
- **THEN** the frontend SHALL send the file to the backend and SHALL NOT directly use Cloudinary API secrets

### Requirement: Image File Validation
The system SHALL validate listing image MIME type, extension, and file size before storing any uploaded image.

#### Scenario: Invalid image type rejected
- **WHEN** a user uploads a non-image file or unsupported image extension
- **THEN** the backend SHALL reject the upload with a validation error and SHALL NOT persist a listing image record

#### Scenario: Oversized image rejected
- **WHEN** a user uploads an image larger than the configured maximum size
- **THEN** the backend SHALL reject the upload with a validation error and SHALL NOT call the storage provider

### Requirement: Listing Image Ownership
The system SHALL allow only the listing-owner Farmer or an Admin to upload or delete images for a listing.

#### Scenario: Other farmer upload blocked
- **WHEN** a Farmer attempts to upload an image for another Farmer's listing
- **THEN** the system SHALL reject the request with a forbidden or not-found response

#### Scenario: Admin manages listing image
- **WHEN** an Admin uploads or deletes an image for any listing
- **THEN** the system SHALL permit the action and persist the listing image change

### Requirement: Multiple Listing Images
The system SHALL support multiple images per listing where feasible and SHALL expose enough metadata for primary image display and deletion.

#### Scenario: Listing returns images
- **WHEN** a client requests listing details
- **THEN** the response SHALL include uploaded listing images with id, URL, primary status, sort order, and created timestamp

#### Scenario: Primary image displayed
- **WHEN** a listing has uploaded images
- **THEN** listing cards and detail pages SHALL display the primary image or the first available uploaded image

### Requirement: Listing Image Frontend
The frontend SHALL provide image upload and preview controls in listing create/edit workflows and SHALL display uploaded images in marketplace listing cards/details.

#### Scenario: Farmer previews uploaded image
- **WHEN** a Farmer uploads a valid listing image in the create/edit form
- **THEN** the UI SHALL show the uploaded image preview and associate the image with the listing

#### Scenario: Upload error displayed
- **WHEN** image upload fails validation or storage configuration checks
- **THEN** the UI SHALL show a clear error message and keep the listing form usable
