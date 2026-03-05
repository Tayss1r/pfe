"""
Seed script to insert sample data for testing.

Run from the backend directory:
    python -m scripts.seed_data
"""

import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models import (
    Client,
    Manufacturer,
    Equipment,
    TechnicalDocument,
    SparePart,
    Role,
)


async def seed_data():
    """Insert sample data into the database."""
    
    async with AsyncSessionLocal() as session:
        print("🌱 Starting database seeding...")

        # Check if data already exists
        result = await session.execute(select(Equipment).limit(1))
        if result.scalar_one_or_none():
            print("⚠️  Sample data already exists. Skipping seed.")
            return

        # =================================================================
        # 1. Create Roles (if not exists)
        # =================================================================
        print("Creating roles...")
        roles_data = [
            {"name": "technicien", "description": "Field technician"},
            {"name": "admin", "description": "System administrator"},
        ]
        
        for role_data in roles_data:
            result = await session.execute(
                select(Role).where(Role.name == role_data["name"])
            )
            if not result.scalar_one_or_none():
                role = Role(**role_data)
                session.add(role)
        
        await session.flush()

        # =================================================================
        # 2. Create Clients
        # =================================================================
        print("Creating clients...")
        clients = [
            Client(
                id=uuid.uuid4(),
                name="Acme Corporation",
                email="support@acme.com",
                phone="+1-555-0100",
                address="123 Business Park, New York, NY 10001",
            ),
            Client(
                id=uuid.uuid4(),
                name="TechStart Inc.",
                email="contact@techstart.io",
                phone="+1-555-0200",
                address="456 Innovation Drive, San Francisco, CA 94105",
            ),
            Client(
                id=uuid.uuid4(),
                name="Global Industries",
                email="service@globalind.com",
                phone="+1-555-0300",
                address="789 Industrial Blvd, Chicago, IL 60601",
            ),
            Client(
                id=uuid.uuid4(),
                name="MediHealth Hospital",
                email="equipment@medihealth.org",
                phone="+1-555-0400",
                address="321 Medical Center Way, Boston, MA 02115",
            ),
        ]
        
        for client in clients:
            session.add(client)
        
        await session.flush()
        print(f"  ✓ Created {len(clients)} clients")

        # =================================================================
        # 3. Create Manufacturers
        # =================================================================
        print("Creating manufacturers...")
        manufacturers = [
            Manufacturer(
                id=uuid.uuid4(),
                name="Samsung Electronics",
                support_email="techsupport@samsung.com",
                support_phone="+1-800-726-7864",
            ),
            Manufacturer(
                id=uuid.uuid4(),
                name="HP Inc.",
                support_email="support@hp.com",
                support_phone="+1-800-474-6836",
            ),
            Manufacturer(
                id=uuid.uuid4(),
                name="Dell Technologies",
                support_email="technical_support@dell.com",
                support_phone="+1-800-624-9896",
            ),
            Manufacturer(
                id=uuid.uuid4(),
                name="Siemens Healthineers",
                support_email="support@siemens-healthineers.com",
                support_phone="+1-888-826-9702",
            ),
        ]
        
        for manufacturer in manufacturers:
            session.add(manufacturer)
        
        await session.flush()
        print(f"  ✓ Created {len(manufacturers)} manufacturers")

        # =================================================================
        # 4. Create Equipment
        # =================================================================
        print("Creating equipment...")
        equipment_list = [
            Equipment(
                id=uuid.uuid4(),
                serial_number="SN-SAM-2024-001",
                brand="Samsung",
                model="Galaxy Tab S9",
                type="Tablet",
                image="/images/equipment/tablet.jpg",
                client_id=clients[0].id,
                manufacturer_id=manufacturers[0].id,
            ),
            Equipment(
                id=uuid.uuid4(),
                serial_number="SN-HP-2024-002",
                brand="HP",
                model="LaserJet Pro MFP M428",
                type="Printer",
                image="/images/equipment/printer.jpg",
                client_id=clients[0].id,
                manufacturer_id=manufacturers[1].id,
            ),
            Equipment(
                id=uuid.uuid4(),
                serial_number="SN-DELL-2024-003",
                brand="Dell",
                model="OptiPlex 7090",
                type="Desktop Computer",
                image="/images/equipment/desktop.jpg",
                client_id=clients[1].id,
                manufacturer_id=manufacturers[2].id,
            ),
            Equipment(
                id=uuid.uuid4(),
                serial_number="SN-DELL-2024-004",
                brand="Dell",
                model="Latitude 5520",
                type="Laptop",
                image="/images/equipment/laptop.jpg",
                client_id=clients[1].id,
                manufacturer_id=manufacturers[2].id,
            ),
            Equipment(
                id=uuid.uuid4(),
                serial_number="SN-HP-2024-005",
                brand="HP",
                model="Elite Display E243",
                type="Monitor",
                image="/images/equipment/monitor.jpg",
                client_id=clients[2].id,
                manufacturer_id=manufacturers[1].id,
            ),
            Equipment(
                id=uuid.uuid4(),
                serial_number="SN-SIEM-2024-006",
                brand="Siemens",
                model="MAGNETOM Altea",
                type="MRI Scanner",
                image="/images/equipment/mri.jpg",
                client_id=clients[3].id,
                manufacturer_id=manufacturers[3].id,
            ),
            Equipment(
                id=uuid.uuid4(),
                serial_number="SN-SAM-2024-007",
                brand="Samsung",
                model="55\" Business Display",
                type="Digital Signage",
                image="/images/equipment/display.jpg",
                client_id=clients[2].id,
                manufacturer_id=manufacturers[0].id,
            ),
        ]
        
        for equipment in equipment_list:
            session.add(equipment)
        
        await session.flush()
        print(f"  ✓ Created {len(equipment_list)} equipment items")

        # =================================================================
        # 5. Create Technical Documents
        # =================================================================
        print("Creating technical documents...")
        documents = [
            # Documents for Printer (equipment_list[1])
            TechnicalDocument(
                id=uuid.uuid4(),
                equipment_id=equipment_list[1].id,
                title="HP LaserJet Pro M428 - User Manual",
                file_path="/docs/hp_m428_manual.pdf",
                document_type="PDF",
            ),
            TechnicalDocument(
                id=uuid.uuid4(),
                equipment_id=equipment_list[1].id,
                title="Toner Replacement Guide",
                file_path="/docs/hp_m428_toner_guide.pdf",
                document_type="PDF",
            ),
            TechnicalDocument(
                id=uuid.uuid4(),
                equipment_id=equipment_list[1].id,
                title="Paper Jam Troubleshooting Video",
                file_path="/videos/hp_paper_jam.mp4",
                document_type="VIDEO",
            ),
            
            # Documents for Desktop (equipment_list[2])
            TechnicalDocument(
                id=uuid.uuid4(),
                equipment_id=equipment_list[2].id,
                title="Dell OptiPlex 7090 - Service Manual",
                file_path="/docs/dell_optiplex_7090_service.pdf",
                document_type="PDF",
            ),
            TechnicalDocument(
                id=uuid.uuid4(),
                equipment_id=equipment_list[2].id,
                title="System Board Diagram",
                file_path="/images/dell_7090_motherboard.jpg",
                document_type="IMAGE",
            ),
            
            # Documents for Laptop (equipment_list[3])
            TechnicalDocument(
                id=uuid.uuid4(),
                equipment_id=equipment_list[3].id,
                title="Dell Latitude 5520 - Quick Start Guide",
                file_path="/docs/dell_latitude_5520_quickstart.pdf",
                document_type="PDF",
            ),
            TechnicalDocument(
                id=uuid.uuid4(),
                equipment_id=equipment_list[3].id,
                title="Battery Replacement Tutorial",
                file_path="/videos/dell_battery_replace.mp4",
                document_type="VIDEO",
            ),
            
            # Documents for MRI Scanner (equipment_list[5])
            TechnicalDocument(
                id=uuid.uuid4(),
                equipment_id=equipment_list[5].id,
                title="MAGNETOM Altea - Technical Specifications",
                file_path="/docs/siemens_altea_specs.pdf",
                document_type="PDF",
            ),
            TechnicalDocument(
                id=uuid.uuid4(),
                equipment_id=equipment_list[5].id,
                title="Safety Guidelines",
                file_path="/docs/siemens_mri_safety.pdf",
                document_type="PDF",
            ),
            TechnicalDocument(
                id=uuid.uuid4(),
                equipment_id=equipment_list[5].id,
                title="System Overview Video",
                file_path="/videos/siemens_altea_overview.mp4",
                document_type="VIDEO",
            ),
        ]
        
        for doc in documents:
            session.add(doc)
        
        await session.flush()
        print(f"  ✓ Created {len(documents)} technical documents")

        # =================================================================
        # 6. Create Spare Parts
        # =================================================================
        print("Creating spare parts...")
        spare_parts = [
            # Spare parts for Printer (equipment_list[1])
            SparePart(
                id=uuid.uuid4(),
                equipment_id=equipment_list[1].id,
                name="CF258A Black Toner Cartridge",
                reference_code="CF258A",
                description="Original HP 58A Black LaserJet Toner Cartridge",
                image="/images/parts/hp_toner.jpg",
            ),
            SparePart(
                id=uuid.uuid4(),
                equipment_id=equipment_list[1].id,
                name="Paper Feed Roller Kit",
                reference_code="RM2-5452-000",
                description="Replacement roller kit for paper tray",
            ),
            SparePart(
                id=uuid.uuid4(),
                equipment_id=equipment_list[1].id,
                name="Fuser Assembly",
                reference_code="RM2-5679-000CN",
                description="110V Fuser Unit",
            ),
            
            # Spare parts for Desktop (equipment_list[2])
            SparePart(
                id=uuid.uuid4(),
                equipment_id=equipment_list[2].id,
                name="8GB DDR4 RAM Module",
                reference_code="SNPVDFYDC/8G",
                description="Dell Memory - 8GB - 1Rx8 DDR4 UDIMM 3200MHz",
            ),
            SparePart(
                id=uuid.uuid4(),
                equipment_id=equipment_list[2].id,
                name="256GB SSD",
                reference_code="400-BDPQ",
                description="M.2 2280 PCIe NVMe SSD",
            ),
            SparePart(
                id=uuid.uuid4(),
                equipment_id=equipment_list[2].id,
                name="Power Supply Unit",
                reference_code="HU260EBS-01",
                description="260W Power Supply",
            ),
            
            # Spare parts for Laptop (equipment_list[3])
            SparePart(
                id=uuid.uuid4(),
                equipment_id=equipment_list[3].id,
                name="Laptop Battery",
                reference_code="JHR7V",
                description="4-Cell 63Whr Internal Battery",
                image="/images/parts/dell_battery.jpg",
            ),
            SparePart(
                id=uuid.uuid4(),
                equipment_id=equipment_list[3].id,
                name="LCD Screen Assembly",
                reference_code="02R7M",
                description="15.6\" FHD Non-Touch LCD Panel",
            ),
            SparePart(
                id=uuid.uuid4(),
                equipment_id=equipment_list[3].id,
                name="Keyboard",
                reference_code="383D7",
                description="US English Backlit Keyboard",
            ),
            
            # Spare parts for MRI Scanner (equipment_list[5])
            SparePart(
                id=uuid.uuid4(),
                equipment_id=equipment_list[5].id,
                name="Gradient Coil Assembly",
                reference_code="10827695",
                description="Main gradient coil for MAGNETOM series",
            ),
            SparePart(
                id=uuid.uuid4(),
                equipment_id=equipment_list[5].id,
                name="RF Body Coil",
                reference_code="10827701",
                description="Transmit/Receive Body Coil",
            ),
        ]
        
        for part in spare_parts:
            session.add(part)
        
        await session.flush()
        print(f"  ✓ Created {len(spare_parts)} spare parts")

        # =================================================================
        # Commit all changes
        # =================================================================
        await session.commit()
        print("\n✅ Database seeding completed successfully!")
        
        print("\n📋 Summary:")
        print(f"   - {len(clients)} clients")
        print(f"   - {len(manufacturers)} manufacturers")
        print(f"   - {len(equipment_list)} equipment items")
        print(f"   - {len(documents)} technical documents")
        print(f"   - {len(spare_parts)} spare parts")
        
        print("\n🔍 Sample equipment to search for:")
        for eq in equipment_list:
            print(f"   - Serial: {eq.serial_number} | {eq.brand} {eq.model} ({eq.type})")


if __name__ == "__main__":
    asyncio.run(seed_data())
