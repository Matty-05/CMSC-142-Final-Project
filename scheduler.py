from datetime import datetime

class Section:
    def __init__(self, subject_name, section_name, start_str, end_str):
        self.subject_name = subject_name
        self.section_name = section_name
        self.start_time = datetime.strptime(start_str, "%H:%M")
        self.end_time = datetime.strptime(end_str, "%H:%M")

    def conflicts_with(self, other_section):
        # Two intervals overlap if the max of their starts is strictly less than the min of their ends.
        # This allows subjects to perfectly touch (e.g., 07:00-08:00 and 08:00-09:00 do NOT conflict)
        return max(self.start_time, other_section.start_time) < min(self.end_time, other_section.end_time)

    def display(self):
        start = self.start_time.strftime("%H:%M")
        end = self.end_time.strftime("%H:%M")
        return f"{self.subject_name} ({self.section_name}): {start} - {end}"


class PreEnlistmentScheduler:
    def __init__(self):
        # This stores ALL inputted sections permanently (until the code restarts)
        self.wishlist = []
        self.required_subjects = set()

    def add_section(self, subject_name, section_name, start_time, end_time):
        try:
            # Parse the strings into datetime objects first
            start_dt = datetime.strptime(start_time, "%H:%M")
            end_dt = datetime.strptime(end_time, "%H:%M")

            # Check if start time is greater than or equal to end time
            if start_dt >= end_dt:
                print(f"\n[!] Error: Start time ({start_time}) must be strictly earlier than End time ({end_time}).")
                return # Stop the function from adding this to the wishlist
            
            # Check if the exact same section already exists in the wishlist
            for sec in self.wishlist:
                if sec.subject_name.lower() == subject_name.lower() and sec.section_name.lower() == section_name.lower():
                    print(f"\n[!] Error: Section '{section_name}' for '{subject_name}' already exists in your wishlist.")
                    return

            # If it passes the check, create and add the section
            new_section = Section(subject_name, section_name, start_time, end_time)
            self.wishlist.append(new_section)
            self.required_subjects.add(subject_name)
            print(f"\n[+] Saved to Wishlist: {new_section.display()}")
            
        except ValueError:
            # This triggers if they type a bad format like "9 PM" instead of "21:00"
            print("\n[!] Error: Invalid time format. Please use HH:MM (e.g., 14:30).")

    def view_wishlist(self):
        print("\n" + "="*40)
        print("----- CURRENT WISHLIST (ALL SAVED) -----")
        print("="*40)
        if not self.wishlist:
            print("[!] Wishlist is empty.")
        else:
            # Group by subject for cleaner viewing
            for subject in sorted(self.required_subjects):
                print(f"\n  {subject} Options:")
                for sec in self.wishlist:
                    if sec.subject_name == subject:
                        print(f"  - {sec.section_name} | {sec.start_time.strftime('%H:%M')} - {sec.end_time.strftime('%H:%M')}")
        print("="*40)

    def delete_section(self):
        if not self.wishlist:
            print("\n[!] Wishlist is empty. There is nothing to delete.")
            return

        # Show the current wishlist so the user knows what they can delete
        self.view_wishlist()
        
        print("\n-- Delete Section Form --")
        subj_to_delete = input("Enter the Subject Name to delete: ").strip()
        sec_to_delete = input("Enter the Section Name to delete: ").strip()

        # Find the specific section in the wishlist (case-insensitive for better UX)
        section_to_remove = None
        for sec in self.wishlist:
            if sec.subject_name.lower() == subj_to_delete.lower() and sec.section_name.lower() == sec_to_delete.lower():
                section_to_remove = sec
                break

        if section_to_remove:
            self.wishlist.remove(section_to_remove)
            print(f"\n[-] Successfully deleted: {section_to_remove.display()}")

            # Check if that was the last section for this specific subject
            still_exists = any(s.subject_name.lower() == subj_to_delete.lower() for s in self.wishlist)
            
            if not still_exists:
                # Remove it from required_subjects to prevent fake conflict errors later
                for req_subj in list(self.required_subjects):
                    if req_subj.lower() == subj_to_delete.lower():
                        self.required_subjects.remove(req_subj)
                        print(f"\n[-] Note: No more sections left for '{req_subj}'. It has been removed from your required subjects.")
        else:
            print(f"\n[!] Error: Could not find '{subj_to_delete} ({sec_to_delete})' in your wishlist. Check spelling.")

    def generate_schedule(self):
        if not self.wishlist:
            print("\n[!] Your wishlist is empty. Please add subjects first.")
            return

        print(f"\n[*] Re-evaluating all {len(self.wishlist)} saved sections...")

        # Greedy Algo: Sort ALL saved sections by Earliest Finish Time
        sorted_sections = sorted(self.wishlist, key=lambda sec: sec.end_time)

        final_schedule = []
        scheduled_subjects = set()

        # The loop evaluates the entire wishlist from scratch every time it runs
        for section in sorted_sections:
            if section.subject_name in scheduled_subjects:
                continue

            has_conflict = False
            for scheduled in final_schedule:
                if section.conflicts_with(scheduled):
                    has_conflict = True
                    break

            if not has_conflict:
                final_schedule.append(section)
                scheduled_subjects.add(section.subject_name)

        self._display_results(final_schedule, scheduled_subjects)

    def _display_results(self, final_schedule, scheduled_subjects):
        print("\n" + "="*40)
        
        if len(scheduled_subjects) == len(self.required_subjects):
            print("----- PERFECTED WEEKLY SCHEDULE -----")
            print("="*40)
            final_schedule.sort(key=lambda sec: sec.start_time)
            for sec in final_schedule:
                print(f"  {sec.display()}")
            print("="*40)
        else:
            print("----- CONFLICT ERROR -----")
            print("="*40)
            missing = self.required_subjects - scheduled_subjects
            print(f"[!] The system could not fit all required subjects.")
            print(f"[!] Missing Subject(s): {', '.join(missing)}")
            print("\n  Partial Schedule Generated:")
            for sec in final_schedule:
                print(f"  - {sec.display()}")
            print("="*40)

def main():
    scheduler = PreEnlistmentScheduler()
    
    while True:
        print("\n--- Pre-Enlistment Scheduler ---")
        print("1. Add a Section to Wishlist")
        print("2. View Current Wishlist")
        print("3. Delete a Section")
        print("4. Load Sample Data")
        print("5. Generate Schedule")
        print("6. Exit")
        
        choice = input("Select an option (1-6): ")
        
        if choice == '1':
            print("\n-- Add Section Form --")
            subj = input("Subject Name (e.g., CMSC 142): ")
            sec = input("Section Name (e.g., Sec 1): ")
            start = input("Start Time (HH:MM, 24hr format): ")
            end = input("End Time (HH:MM, 24hr format): ")
            scheduler.add_section(subj, sec, start, end)
            
        elif choice == '2':
            scheduler.view_wishlist()
            
        elif choice == '3':
            scheduler.delete_section()

        elif choice == '4':
            print("\nLoading pre-made schedules...")
            scheduler.add_section("Math 53", "Sec-A", "08:30", "10:00")
            scheduler.add_section("Math 53", "Sec-B", "14:00", "16:30")
            scheduler.add_section("CMSC 142", "Sec-A", "07:00", "08:00")
            scheduler.add_section("CMSC 126", "Sec-A", "08:00", "09:00")
            
        elif choice == '5':
            scheduler.generate_schedule()
            
        elif choice == '6':
            print("Exiting application...")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()