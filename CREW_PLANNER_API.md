# Crew Planner API Documentation

## Overview

The Crew Planner API provides endpoints for managing crew members, positions, assignments, and accommodations for a surf camp operation. It includes features for tracking crew scheduling and preventing accommodation conflicts.

## Base URL

All endpoints are prefixed with `/crew`

## Team Types

The following team types are supported:
- `SURF` - Surf instructors and staff
- `SKATE` - Skateboarding instructors
- `YOGA` - Yoga instructors
- `KITCHEN` - Kitchen staff
- `CLEANING` - Cleaning staff
- `RECEPTION` - Reception staff

## Endpoints

### Crew Members

#### GET /crew/crew
Get all crew members, optionally filtered by team.

**Query Parameters:**
- `team` (optional): Filter by team (e.g., `SURF`, `YOGA`)

**Response:** Array of crew members
```json
[
  {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "123-456-7890",
    "team": "SURF",
    "skills": "Advanced surf instruction",
    "notes": "Available weekends"
  }
]
```

#### POST /crew/crew
Create a new crew member.

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "123-456-7890",
  "team": "SURF",
  "skills": "Advanced surf instruction",
  "notes": "Available weekends"
}
```

**Response:** Created crew member (201)

---

### Positions

#### GET /crew/positions
Get all positions, optionally filtered by team.

**Query Parameters:**
- `team` (optional): Filter by team

**Response:** Array of positions
```json
[
  {
    "id": 1,
    "name": "Lead Surf Instructor",
    "team": "SURF",
    "description": "Main instructor for advanced groups"
  }
]
```

#### POST /crew/positions
Create a new position.

**Request Body:**
```json
{
  "name": "Lead Surf Instructor",
  "team": "SURF",
  "description": "Main instructor for advanced groups"
}
```

**Response:** Created position (201)

---

### Crew Assignments

#### POST /crew/assign-crew
Assign a crew member to a position on a specific date.

**Request Body:**
```json
{
  "crew_member_id": 1,
  "position_id": 1,
  "assignment_date": "2025-06-15"
}
```

**Response:** Created assignment (201)
```json
{
  "id": 1,
  "crew_member_id": 1,
  "position_id": 1,
  "assignment_date": "2025-06-15",
  "message": "Crew assignment created successfully"
}
```

**Errors:**
- 404: Crew member or position not found
- 500: Server error

#### GET /crew/crew-calendar
Get daily crew planning overview for a date range.

**Query Parameters:**
- `start` (required): Start date in format `yyyy-mm-dd` (e.g., `2025-04-01`)
- `end` (required): End date in format `yyyy-mm-dd` (e.g., `2025-09-30`)
- `team` (optional): Filter by team

**Response:** Calendar with assignments grouped by date
```json
{
  "start_date": "2025-06-01",
  "end_date": "2025-06-30",
  "team": "SURF",
  "calendar": {
    "2025-06-01": [
      {
        "id": 1,
        "crew_member": {
          "id": 1,
          "first_name": "John",
          "last_name": "Doe",
          "team": "SURF"
        },
        "position": {
          "id": 1,
          "name": "Lead Surf Instructor",
          "team": "SURF"
        },
        "assignment_date": "2025-06-01"
      }
    ],
    "2025-06-02": []
  }
}
```

**Errors:**
- 400: Invalid date range (start date after end date)

---

### Accommodations

#### GET /crew/accommodations
Get all accommodations.

**Response:** Array of accommodations
```json
[
  {
    "id": 1,
    "name": "Tent A",
    "accommodation_type": "tent",
    "capacity": 2,
    "notes": "Near the beach"
  }
]
```

#### POST /crew/accommodations
Create a new accommodation.

**Request Body:**
```json
{
  "name": "Tent A",
  "accommodation_type": "tent",
  "capacity": 2,
  "notes": "Near the beach"
}
```

**Response:** Created accommodation (201)

#### POST /crew/assign-accommodation
Assign accommodation to a crew member with conflict checking.

**Request Body:**
```json
{
  "crew_member_id": 1,
  "accommodation_id": 1,
  "start_date": "2025-06-01",
  "end_date": "2025-06-30"
}
```

**Response:** Created accommodation assignment (201)
```json
{
  "id": 1,
  "crew_member_id": 1,
  "accommodation_id": 1,
  "start_date": "2025-06-01",
  "end_date": "2025-06-30",
  "message": "Accommodation assignment created successfully"
}
```

**Validation Rules:**
1. **No Double Booking**: The accommodation must have available capacity
2. **No Tent Changes**: Crew member cannot be assigned to a different accommodation during an overlapping period

**Errors:**
- 400: Validation error (capacity exceeded or tent change conflict)
- 404: Crew member or accommodation not found
- 500: Server error

#### GET /crew/accommodation-assignments
Get accommodation assignments, optionally filtered by date range.

**Query Parameters:**
- `start` (optional): Start date filter
- `end` (optional): End date filter

**Response:** Array of accommodation assignments
```json
[
  {
    "id": 1,
    "crew_member_id": 1,
    "accommodation_id": 1,
    "start_date": "2025-06-01",
    "end_date": "2025-06-30",
    "crew_member": {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe"
    },
    "accommodation": {
      "id": 1,
      "name": "Tent A",
      "type": "tent"
    }
  }
]
```

---

## Example Usage

### Complete Workflow Example

```bash
# 1. Create a crew member
curl -X POST http://localhost:8000/crew/crew \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@test.com",
    "phone": "123-456-7890",
    "team": "SURF",
    "skills": "Advanced surf instruction",
    "notes": "Available weekends"
  }'

# 2. Create a position
curl -X POST http://localhost:8000/crew/positions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lead Surf Instructor",
    "team": "SURF",
    "description": "Main instructor for advanced groups"
  }'

# 3. Assign crew to position
curl -X POST http://localhost:8000/crew/assign-crew \
  -H "Content-Type: application/json" \
  -d '{
    "crew_member_id": 1,
    "position_id": 1,
    "assignment_date": "2025-06-15"
  }'

# 4. Get crew calendar for June 2025
curl "http://localhost:8000/crew/crew-calendar?start=2025-06-01&end=2025-06-30"

# 5. Filter crew calendar by SURF team
curl "http://localhost:8000/crew/crew-calendar?start=2025-06-01&end=2025-06-30&team=SURF"

# 6. Create accommodation
curl -X POST http://localhost:8000/crew/accommodations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tent A",
    "accommodation_type": "tent",
    "capacity": 2,
    "notes": "Near the beach"
  }'

# 7. Assign accommodation
curl -X POST http://localhost:8000/crew/assign-accommodation \
  -H "Content-Type: application/json" \
  -d '{
    "crew_member_id": 1,
    "accommodation_id": 1,
    "start_date": "2025-06-01",
    "end_date": "2025-06-30"
  }'
```

---

## Database Schema

The crew planner uses the following database tables:

- `crew_members` - Stores crew member information
- `positions` - Stores position definitions
- `crew_assignments` - Tracks crew member assignments to positions
- `accommodations` - Stores accommodation information
- `accommodation_assignments` - Tracks crew member accommodation assignments

To create the database schema, run:
```bash
python create_db.py
```

---

## Testing

### Unit Tests
Run unit tests with:
```bash
python -m unittest test.test_crew_service -v
```

### Manual Testing
Run the manual test script:
```bash
python test_crew_manual.py
```

This will create sample data and test all functionality including conflict validation.
